def all_eq(lst):
    lst_cop = []
    lst_cop.extend(lst)
    tmp = lst_cop[0]
    for i in range(1,len(lst_cop)):
        if len(lst_cop[i]) > len(tmp):
            tmp = lst_cop[i]
    for i in range(len(lst_cop)):
        #if len(lst[i]) < len(tmp):
        lst_cop[i] += (len(tmp) - len(lst_cop[i])) * '_'
    return lst_cop
lst = ['qqq', 'wwww', 'eeeee', 'rrrrr']
print(f' early list{lst}')
one_eq = all_eq(lst)
print(f' ending list{one_eq}')