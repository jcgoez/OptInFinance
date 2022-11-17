# Example 2.1 from Optimization methods in finance, 2ed
from pyomo.environ import *


infinity = float('inf')

# Create a abstract model
model = AbstractModel(name='Funds')

#Define sets
# Funds
model.F = Set()
# Stocks requirenments
model.N = Set()

# Defining model parameters
# Returns of each fund
model.r    = Param(model.F, name="Returns")
# Compositin of each fund
model.a    = Param(model.N, model.F, within=NonNegativeReals, name="CompositionFunds")
# Upper bound for the investment in each type of stock
model.Nmax = Param(model.N, within=NonNegativeReals, default=infinity)
# budget to be invested
model.Budget = Param(within=PositiveReals)

#Defining the model variables
# Amount (in $1000s) invested in fund i
model.x = Var(model.F, within=NonNegativeReals)

# Objective function
# Maximize the return of the portfolio
def returnFunds_rule(model):
    return sum(model.r[j]*model.x[j] for j in model.F)
model.returnFunds = Objective(rule=returnFunds_rule, sense=maximize)

# Constraints
# Impose the limits on the type of stocks
def cap_rule(model, i):
    value = sum(model.a[i,j]*model.x[j] for j in model.F)
    return inequality(model.Nmax[i]*model.Budget, value)
model.cap_limit = Constraint(model.N, rule=cap_rule)

# Limit the budget constraint
def budget_rule(model):
    return sum(model.x[j] for j in model.F) <= model.Budget
model.budget = Constraint(rule=budget_rule)

# Instantiate the model with specific data
instance = model.create_instance("fundsPortfolio1.dat")

# This is needed for obtaining the dual variables later
instance.dual = Suffix(direction=Suffix.IMPORT)

# Select the solver
opt = SolverFactory('gurobi')
# Examples of solver parameters
opt.options["solnsens"] = 1
opt.options['outlev'] = 1
opt.options["resultfile"] = "C:/Users/s12953/Documents/repositories/OptInFinance/src/fundsProblem.sol"

# Solving the instance
results = opt.solve(instance)#, tee=True)

###### Printing the results ###############
instance.display()

# for v in instance.component_objects(Var, active=True):
#     print("   Variable",v)  
#     for index in v:
#         print (f"{'':6} {index:10} {value(v[index]):<10.5f}") 

print (f'\n\n{"":6} {"Index":<10} {"Dual":<10} {"Slack":<10}')
for c in instance.component_objects(Constraint, active=True):
    print ("   Constraint",c)
    for index in c:
        if index != None:
            print (f'{"":6} {index:10} {instance.dual[c[index]]:<10.5f} {c[index].lslack():<10.5f}')
        else:
            print (f'{"":6} {"":10} {instance.dual[c[index]]:<10.5f}  {c[index].uslack():<10.5f}')





