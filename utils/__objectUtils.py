
def hasattrdeep(object, attributes: list[str]) -> bool:
    if len(attributes) == 0:
        return True
    if attributes[0] in object:
        return hasattrdeep(object[attributes[0]], attributes[1:])
    return False

def traverseDictAndUpdateField(fieldPath, newValue, dict):
            if len(fieldPath) == 1:
                dict[fieldPath[0]] = newValue
                return dict
            field = fieldPath.pop(0)
            if field not in dict:
                dict[field] = {}
            if not type(dict[field]) == dict:
                raise TypeError(f"Field '{field}' cannot be updated as it is not a dict")
            dict[field] = traverseDictAndUpdateField(fieldPath, newValue, dict[field])
            return dict