class MyClass:
    my_class_list = []

    def __init__(self, number, lst=[]) -> None:
        self.number = number
    
    def add_obj(self):
        self.number = num
        MyClass.my_class_list.append(self)
    
my_objects = []

for i in range(10):
    my_objects.append(MyClass.add_obj(i, i))

for obj in my_objects:
    print(type(obj.number))
