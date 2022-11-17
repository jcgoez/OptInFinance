# Example 3.1 Bond dedication. From: Optimization methods in finance, 2ed
from pyomo.environ import *


infinity = float('inf')

# Create a abstract model
model = AbstractModel(name='Bond dedication')

#Define sets
# Bonds
model.B = Set()
# Periods
model.P = Set()

# Defining model parameters
# Requirenments of each fund
model.l    = Param(model.P, name="Requirenments")
# Bonds prices
model.p    = Param(model.B, name="Prices")
# Bonds flows
model.f    = Param(model.B, model.P, within=NonNegativeReals, name="Flows")

#Defining the model variables
# Amount (in $1000s) invested in fund i
model.x = Var(model.B, within=NonNegativeReals)
model.s = Var(model.P, within=NonNegativeReals)

# Objective function
# Maximize the return of the portfolio
def costBonds_rule(model):
    return sum(model.p[i]*model.x[i] for i in model.B)
model.costBonds = Objective(rule=costBonds_rule)

# Constraints
#Year 1 balance
def year1_balance(model):
    return sum(model.f[i,1]*model.x[i] for i in model.B if model.f[i,1] > 0) - model.s[1] == model.l[1] 
model.year1_balance = Constraint(rule=year1_balance)

# Balance each year > 1
def cap_rule(model, j):
    return sum(model.f[i,j]*model.x[i] for i in model.B if model.f[i,1] > 0) + model.s[j-1] - model.s[j] == model.l[j] 
model.cap_limit = Constraint(model.P - Set(initialize=[1]), rule=cap_rule)

# Instantiate the model with specific data
instance = model.create_instance("dedication.dat")

# This is needed for obtaining the dual variables later
instance.dual = Suffix(direction=Suffix.IMPORT)

# Select the solver
opt = SolverFactory('gurobi')

# Solving the instance
results = opt.solve(instance, tee=True)

instance.display()

print (f'\n\n{"":6} {"Index":<10} {"Dual":<10} {"Slack":<10}')
for c in instance.component_objects(Constraint, active=True):
    print ("   Constraint",c)
    for index in c:
        if index != None:
            print (f'{"":6} {index:10} {instance.dual[c[index]]:<10.5f} {c[index].lslack():<10.5f}')
        else:
            print (f'{"":6} {"":10} {instance.dual[c[index]]:<10.5f}  {c[index].uslack():<10.5f}')
