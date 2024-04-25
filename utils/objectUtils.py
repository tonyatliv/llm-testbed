
def hasattrdeep(object, attributes: list[str]) -> bool:
    if len(attributes) == 0:
        return True
    if attributes[0] in object:
        return hasattrdeep(object[attributes[0]], attributes[1:])
    return False
