from yaml import safe_load

with open("../vars/params.yaml", "r", encoding='utf-8') as handle:
    data = safe_load(handle)
    print(data)

values = list()

for i in data['devices']:
    for j in range(int(i['qty'])):
        values.append(i['size_gb'])

first_dev_id_dec = int('0x000A', 16)
dev_id_list = []
for i in range(len(values)):
    dev_id = first_dev_id_dec + i
    dev_id_hex = hex(dev_id)
    dev_id_list.append(dev_id_hex)
print(values)
a = list(zip(dev_id_list, values))

print(a)


