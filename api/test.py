def toPercent(num):
    num = num*100
    num = round(num, 4)
    result = str(num)+'%'
    return result

print(toPercent(-1.2355353))