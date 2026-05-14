import json


def parse_template(template_str):
    """Parse the template string into a list of keys and indices."""
    path = []
    stack = []
    i = 0
    n = len(template_str)

    while i < n:
        if template_str[i] == '{' or template_str[i] == '[':
            # Push to stack
            stack.append(template_str[i])
            i += 1
        elif template_str[i] == '}' or template_str[i] == ']':
            # Pop from stack
            if stack:
                stack.pop()
            i += 1
        elif template_str[i] == '"' or template_str[i] == "'":
            # Extract key
            j = i + 1
            while j < n and template_str[j] != template_str[i]:
                j += 1
            key = template_str[i+1:j]
            path.append(key)
            i = j + 1
        elif template_str[i].isdigit():
            # Extract index
            j = i
            while j < n and template_str[j].isdigit():
                j += 1
            index = int(template_str[i:j])
            path.append(index)
            i = j
        elif template_str[i] in ',:':
            i += 1
        else:
            i += 1
    print(f"{path=}")
    return path


def get_value_by_template(payload_json, template_str):
    """Extract value from JSON using the parsed path."""
    try:
        data = json.loads(payload_json)
        path = parse_template(template_str)

        current = data
        for element in path:
            if isinstance(current, dict) and isinstance(element, str):
                current = current[element]
            elif isinstance(current, list) and isinstance(element, int):
                current = current[element]
            else:
                raise KeyError(f"Invalid path element: {element}")
        return current
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        return f"Error: {e} {payload_json=}"


# Example Usage
# real_payload = '{"key1": {"key2": ' \
#                '["val0", "val1", "val2", {"key3": ["val_in_dict"]},' \
#                ' "TARGET_VALUE"]}}'
# my_template = "{'key1':{'key2':[3, {'key3':[0]}]}}"

# result = get_value_by_template(real_payload, my_template)
# print(f"Extracted Value: {result}")
