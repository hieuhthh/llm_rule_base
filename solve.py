import json
from multiprocessing.util import is_abstract_socket_namespace

# --- Expression Parsing Utilities ---

def tokenize(expr):
    """
    Tokenizes the input expression string.
    Recognizes parentheses, operators, and alphanumeric symbols.
    """
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in ['(', ')', '∧', '∨', '¬']:
            tokens.append(c)
            i += 1
        else:
            # Accumulate alphanumeric characters (e.g., variable names)
            j = i
            while j < len(expr) and expr[j].isalnum():
                j += 1
            tokens.append(expr[i:j])
            i = j
    return tokens

def parse_expression(tokens):
    """
    Parses an expression using a recursive descent parser.
    Grammar:
      expression := or_expr
      or_expr := and_expr { '∨' and_expr }*
      and_expr := not_expr { '∧' not_expr }*
      not_expr := '¬' not_expr | atom
      atom := VARIABLE | '(' expression ')'
    Returns an AST and any remaining tokens.
    """
    expr, tokens = parse_or(tokens)
    return expr, tokens

def parse_or(tokens):
    expr, tokens = parse_and(tokens)
    while tokens and tokens[0] == '∨':
        tokens.pop(0)  # remove '∨'
        right, tokens = parse_and(tokens)
        expr = ('or', expr, right)
    return expr, tokens

def parse_and(tokens):
    expr, tokens = parse_not(tokens)
    while tokens and tokens[0] == '∧':
        tokens.pop(0)  # remove '∧'
        right, tokens = parse_not(tokens)
        expr = ('and', expr, right)
    return expr, tokens

def parse_not(tokens):
    if tokens and tokens[0] == '¬':
        tokens.pop(0)
        expr, tokens = parse_not(tokens)
        return ('not', expr), tokens
    else:
        return parse_atom(tokens)

def parse_atom(tokens):
    if not tokens:
        raise ValueError("Unexpected end of tokens in atom parsing")
    token = tokens.pop(0)
    if token == '(':
        expr, tokens = parse_expression(tokens)
        if not tokens or tokens[0] != ')':
            raise ValueError("Missing closing parenthesis")
        tokens.pop(0)  # remove ')'
        return expr, tokens
    else:
        return ('var', token), tokens

def parse_logical_expr(expr_str):
    """
    Parses a logical expression string and returns its AST.
    """
    tokens = tokenize(expr_str)
    ast, remaining = parse_expression(tokens)
    if remaining:
        raise ValueError(f"Unexpected tokens remaining: {remaining}")
    return ast

# --- Evaluator ---

def evaluate_expr(ast, facts):
    """
    Evaluates the AST expression given a dictionary of facts.
    For an undefined variable, we assume it is False.
    """
    node_type = ast[0]
    if node_type == 'var':
        return facts.get(ast[1], False)
    elif node_type == 'not':
        return not evaluate_expr(ast[1], facts)
    elif node_type == 'and':
        return evaluate_expr(ast[1], facts) and evaluate_expr(ast[2], facts)
    elif node_type == 'or':
        return evaluate_expr(ast[1], facts) or evaluate_expr(ast[2], facts)
    else:
        raise ValueError(f"Unknown AST node type: {node_type}")

def literal_from_ast(ast):
    """
    Extracts a literal from an AST assumed to be either an atom or a negated atom.
    Returns (variable, truth_value). For example:
      ('var', 'A')        -> ('A', True)
      ('not', ('var','A')) -> ('A', False)
    """
    if ast[0] == 'var':
        return ast[1], True
    elif ast[0] == 'not' and ast[1][0] == 'var':
        return ast[1][1], False
    else:
        raise ValueError("Conclusion must be a literal (atom or its negation)")

# --- Forward Chaining Solver ---

def solve_rule_base(rule_base):
    """
    Given a rule base dictionary with:
      - "logical_statements": descriptive statements (ignored in solving)
      - "rule_representation": a list of symbolic rules (axioms or implications)
      - "answer_logical_statement": the target literal (e.g., "G" or "¬G")
      
    This function parses the rules, applies a forward-chaining algorithm using all logical symbols,
    and returns a detailed derivation.
    """
    steps = []
    # facts: dictionary mapping variable name to boolean value
    facts = {}

    # Process axioms (rules without an implication arrow)
    for rule in rule_base["rule_representation"]:
        if "→" not in rule:
            rule = rule.strip()
            if not rule:
                continue
            # Parse the axiom as a logical expression.
            try:
                ast = parse_logical_expr(rule)
                var, value = literal_from_ast(ast)
                if var not in facts:
                    facts[var] = value
                    # steps.append(f"Added axiom: {rule} as {var} = {value}")
                    steps.append(f"{var} = {value}")
                else:
                    # steps.append(f"Axiom: {rule} already present as {var} = {facts[var]}")
                    pass
            except Exception as e:
                steps.append(f"Skipping axiom '{rule}': {e}")

    # steps.append(f"Initial facts: {facts}")

    # Prepare implication rules: list of tuples (premise_ast, conclusion_literal, original_rule)
    imp_rules = []
    for rule in rule_base["rule_representation"]:
        if "→" in rule:
            parts = rule.split("→")
            if len(parts) != 2:
                steps.append(f"Invalid rule format (should have one '→'): {rule}")
                continue
            premise_str = parts[0].strip()
            conclusion_str = parts[1].strip()
            try:
                premise_ast = parse_logical_expr(premise_str)
                conclusion_ast = parse_logical_expr(conclusion_str)
                conclusion_literal = literal_from_ast(conclusion_ast)
                imp_rules.append((premise_ast, conclusion_literal, rule))
                # steps.append(f"Parsed implication rule: {rule}")
            except Exception as e:
                steps.append(f"Error parsing rule '{rule}': {e}")

    # Forward chaining loop
    added_new = True
    while added_new:
        added_new = False
        for premise_ast, (conc_var, conc_val), orig_rule in imp_rules:
            # Evaluate the premise using current facts.
            if evaluate_expr(premise_ast, facts):
                # If the conclusion variable is not set, add it.
                if conc_var not in facts:
                    facts[conc_var] = conc_val
                    added_new = True
                    # steps.append(f"Rule '{orig_rule}' triggered: premises true, so set {conc_var} = {conc_val}")
                    steps.append(f"'{orig_rule}' so {conc_var} = {conc_val}")
                # If it is set but with a different value, note a contradiction.
                elif facts[conc_var] != conc_val:
                    steps.append(f"Contradiction detected for {conc_var}: existing value {facts[conc_var]}, rule '{orig_rule}' suggests {conc_val}")
        if not added_new:
            # steps.append("No new facts derived in this iteration. End.")
            steps.append("End.")

    # Check the answer logical statement
    answer = rule_base.get("answer_logical_statement", "").strip()
    # The answer might be a literal like "G" or "¬G". Parse it.
    try:
        answer_ast = parse_logical_expr(answer)
        ans_var, ans_val = literal_from_ast(answer_ast)
    except Exception as e:
        steps.append(f"Error parsing answer logical statement '{answer}': {e}")
        ans_var, ans_val = None, None

    is_answer_true = None

    if ans_var is not None:
        if ans_var in facts and facts[ans_var] == ans_val:
            result = f"'{answer}' is True."
            is_answer_true = True
        else:
            result = f"'{answer}' is False."
            is_answer_true = False
    else:
        result = "Invalid answer logical statement."

    return {
        "result": result,
        "facts": facts,
        "steps": steps,
        "is_answer_true": is_answer_true,
    }

if __name__ == '__main__':
    from llm_rule_base import generate_json_rule_base
    
    # problem_input = "Proof that Vietnam is in Southeast Asia."
    problem_input = "Is Hồ Chí Minh city the capital of Vietnam?"
    
    json_rule_base = generate_json_rule_base(problem_input)
    
    print("Solving:", problem_input)
    print(json.dumps(json_rule_base, indent=2, ensure_ascii=False))
    print('-'*20)
    
    dict_result = solve_rule_base(json_rule_base)
    print(json.dumps(dict_result, indent=2, ensure_ascii=False))
