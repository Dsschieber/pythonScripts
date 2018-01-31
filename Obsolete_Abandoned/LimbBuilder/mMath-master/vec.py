import math

class Vec (object):
    """
    This is a vector class that works in a friendly maya way, aka you can 
    get a translation value and initialize directly a Vec class
    """
    def __init__(self, values):
        """
        This is the constructor

        Args:
        
        :values: list[float], the values to initialize the vector with 
        """ 
        self.values = values
    
    def as_list(self):
        """
        This function returns the content of the vector as a list

        This function is kept moslty for consistency with the other vector 
        class, keeping a uniform and consistant class interface
        """

        return self.values

    def dot(self , V):
        """
        This procedure performs a dot product with the given vector

        Args:

        :V: Vec, second vector to perform the operation with

        :return: float
        """
        
        return sum([self.values[x] * V[x] for x in range(len(self))])
        
        
    def cross(self , V):
        """
        This procedure performs the cross product on the two vectors , 
        the two vectors need lenght 3
        
        Args:

        :V: Vec, second vector to perform the operation with

        :return: Vec instance
        """
        assert len(self) == 3  and  len(V) == 3
        
        A = self.values
        
        x = (A[1] *V[2]) - (A[2] *V[1])
        y = (A[2] *V[0]) - (A[0] *V[2])
        z = (A[0] *V[1]) - (A[1] *V[0])
        
        return Vec([x,y,z])
    

    def length(self):
        """
        Return the magnitude of the vector
        
        :return: float
        """
        return math.sqrt(sum(x*x for x in self.values))
        
        
    def normalize(self):
        """
        Return the normalized image of  the class
        
        :return: Vec instance
        """
        tempLen = self.length()
        
        return Vec([x/tempLen for x in self.values])
        
    def __getitem__ (self , index):
        """
        The indexing operator

        Args:
        
        :index: the index to acces 
        """
        return self.values[index]
        
        
    def __setitem__ (self , index , value):
        """
        This procedure allow item set with indexing

        Args:

        :index: int , the index to access
        :value: float , the value To set to given index  
        """
        self.values[index] = value
        
        
    def __neg__ (self):
        """
        This procedure returns the negation of the vector

        :return: Vec instance
        """
        return Vec([ -1.0 * x for x in self.values])
    
    def __eq__ (self , V):
        """
        This procedure checks if this vector is equal to the given one

        Args:

        :V: Vec() , the vector to check agains

        :return : bool 
        """
        for i,v in enumerate(V) :
            
            if self.values[i] != v :
                return False
        
        return True
        
    def __radd__(self, other):
        "Hack to allow sum(...) to work with vectors"
        if other == 0:
            return self   
        
    def __len__(self):
        """
        This procedure returns the length of the vector

        :return: int
        """ 
        return len(self.values)
        
    def __add__(self  ,V):
        """
        This procedure sums the two vectors togheter

        Args:

        :V: Vec() the vector to sum

        :return : Vec()
        """
        assert len(self) == len(V)
        
        return Vec([self.values[x] + V[x] for x in range(len(self))])
        
    def __sub__(self ,V):
        """
        This procedure subtracts two vectors
        
        Args:

        :V: Vec() the vector to subtract

        :return : Vec()
        """
        return self +(-V)
    
    def __str__(self):
        """
        Pretty print of the class
        """
        return str([x for x in self.values])

    def __mul__(self , V):
        """
        This procedure implements the * operator performing a dot product
        
        Args:

        :V: Vec() , the other vector to use for the computation\
        
        :return: Vec()
        """ 
        return self.dot(V)
        

    
    def __rmul__ (self, scal):
        """
        Right multiplication , assuming int or float , performing scalar multiplication
        
        Args:

        :scal: int/float , scalar value for the operation

        :return: Vec instance
        """ 
        return Vec([ x * scal for x in self.values])
       
    def __xor__ (self , V):
        """
        Cross product operator 

        Args:

        :V: Vec, the second vector for the operation

        :return: Vec
        """
        return self.cross(V)
        
