#create parent class whose method is called by your class 
class parent:
    def sum(self,a,b):
        return a+b
class your_class:
    def Fun(self,a,b):
        self.a=a
        self.b=b
        '''
        we can call method of another class
        by using their class name and function with dot operator.
        '''
        x=parent.sum(self,a,b)
        print("sum=",x)
#class object of child class or 
ob=your_class()

x=int(input("enter 1st no.\n"))

y=int(input("enter 2nd no.\n"))

#fuction call of your class
ob.Fun(x,y)