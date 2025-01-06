# Import necessary libraries
from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    DECIMAL,
    CheckConstraint,
    Time,
    Text,
    UniqueConstraint,
    PrimaryKeyConstraint,
    CHAR,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Initialize Faker and SQLAlchemy
fake = Faker()
Faker.seed(0)

engine = create_engine("mysql+pymysql://root:asdzxc.62001@localhost/bankingsystem")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define ORM models for each table

# 1. Branch
class Branch(Base):
    __tablename__ = 'branch'
    BranchID = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Status = Column(String(50), nullable=False)
    __table_args__ = (
        CheckConstraint("Status IN ('Active', 'Inactive', 'Closed')", name='chk_status'),
    )

    addresses = relationship('BranchAddress', back_populates='branch')
    emails = relationship('BranchEmail', back_populates='branch')
    phones = relationship('BranchPhone', back_populates='branch')
    accounts = relationship('BankAccount', back_populates='branch')
    lockerbranches = relationship('LockerBranch', back_populates='branch')

# 2. BranchAddress
class BranchAddress(Base):
    __tablename__ = 'branchaddress'
    Street = Column(String(100), primary_key=True)
    City = Column(String(50), primary_key=True)
    State = Column(String(50), primary_key=True)
    ZipCode = Column(String(10), primary_key=True)
    Country = Column(String(50), primary_key=True)
    BranchID = Column(Integer, ForeignKey('branch.BranchID'))

    branch = relationship('Branch', back_populates='addresses')

# 3. BranchEmail
class BranchEmail(Base):
    __tablename__ = 'branchemail'
    Email = Column(String(255), primary_key=True)
    BranchID = Column(Integer, ForeignKey('branch.BranchID'))

    branch = relationship('Branch', back_populates='emails')

# 4. BranchPhone
class BranchPhone(Base):
    __tablename__ = 'branchphone'
    PhoneNumber = Column(String(20), primary_key=True)
    BranchID = Column(Integer, ForeignKey('branch.BranchID'))

    branch = relationship('Branch', back_populates='phones')

# 5. RoleStatus
class RoleStatus(Base):
    __tablename__ = 'rolestatus'
    Name = Column(String(100), primary_key=True)
    Status = Column(String(50), nullable=False)
    RoleDescription = Column(Text)

# 6. Customer
class Customer(Base):
    __tablename__ = 'customer'
    CustomerID = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Street = Column(String(100), nullable=False)
    City = Column(String(50), nullable=False)
    State = Column(String(50), nullable=False)
    ZipCode = Column(String(10), nullable=False)
    DateOfBirth = Column(Date, nullable=False)
    Gender = Column(CHAR(1), CheckConstraint("Gender IN ('M', 'F')"))

    emails = relationship('CustomerEmail', back_populates='customer')
    phones = relationship('CustomerPhone', back_populates='customer')
    national_ids = relationship('CustomerNationalID', back_populates='customer')
    accounts = relationship('BankAccount', back_populates='customer')
    loans = relationship('Loan', back_populates='customer')
    lockercustomers = relationship('LockerCustomer', back_populates='customer')
    assists = relationship('Assist', back_populates='customer')

# 7. CustomerEmail
class CustomerEmail(Base):
    __tablename__ = 'customeremail'
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'), primary_key=True)
    Email = Column(String(100), primary_key=True)

    customer = relationship('Customer', back_populates='emails')

# 8. CustomerPhone
class CustomerPhone(Base):
    __tablename__ = 'customerphone'
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'), primary_key=True)
    PhoneNumber = Column(String(15), primary_key=True)

    customer = relationship('Customer', back_populates='phones')

# 9. CustomerNationalID
class CustomerNationalID(Base):
    __tablename__ = 'customernationalid'
    NationalID = Column(String(20), primary_key=True)
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'), nullable=False)

    customer = relationship('Customer', back_populates='national_ids')

# 10. RoleName
class RoleName(Base):
    __tablename__ = 'rolename'
    RoleID = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)

    employees = relationship('Employee', back_populates='role')
    rolepermissions = relationship('RolePermission', back_populates='role')

# 11. Employee
class Employee(Base):
    __tablename__ = 'employee'
    EmpID = Column(Integer, primary_key=True)
    Name = Column(String(100), nullable=False)
    Street = Column(String(100), nullable=False)
    City = Column(String(50), nullable=False)
    State = Column(String(50), nullable=False)
    ZipCode = Column(String(10), nullable=False)
    DateOfBirth = Column(Date, nullable=False)
    RoleID = Column(Integer, ForeignKey('rolename.RoleID'), nullable=False)
    Gender = Column(CHAR(1), CheckConstraint("Gender IN ('M', 'F')"))

    role = relationship('RoleName', back_populates='employees')
    emails = relationship('EmployeeEmail', back_populates='employee')
    phones = relationship('EmployeePhone', back_populates='employee')
    national_ids = relationship('EmployeeNationalID', back_populates='employee')
    loans = relationship('Loan', back_populates='employee')
    assists = relationship('Assist', back_populates='employee')

# 12. EmployeeNationalID
class EmployeeNationalID(Base):
    __tablename__ = 'employeenationalid'
    NationalID = Column(String(20), primary_key=True)
    EmpID = Column(Integer, ForeignKey('employee.EmpID'))

    employee = relationship('Employee', back_populates='national_ids')

# 13. EmployeeEmail
class EmployeeEmail(Base):
    __tablename__ = 'employeeemail'
    EmpID = Column(Integer, ForeignKey('employee.EmpID'), primary_key=True)
    Email = Column(String(100), primary_key=True)

    employee = relationship('Employee', back_populates='emails')

# 14. EmployeePhone
class EmployeePhone(Base):
    __tablename__ = 'employeephone'
    EmpID = Column(Integer, ForeignKey('employee.EmpID'), primary_key=True)
    PhoneNumber = Column(String(15), primary_key=True)

    employee = relationship('Employee', back_populates='phones')

# 15. BankAccount
class BankAccount(Base):
    __tablename__ = 'bankaccount'
    AccID = Column(Integer, primary_key=True)
    Type = Column(String(50), nullable=False)
    SetupDate = Column(Date, nullable=False)
    Balance = Column(DECIMAL(15, 2), nullable=False)
    Status = Column(String(50), nullable=False)
    BranchID = Column(Integer, ForeignKey('branch.BranchID'))
    LastActivityDate = Column(Date, nullable=False)
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'))

    branch = relationship('Branch', back_populates='accounts')
    customer = relationship('Customer', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account', foreign_keys='Transaction.AccID')
    fixed_investments = relationship('FixedRateInvestment', back_populates='account')
    variable_investments = relationship('VariableRateInvestment', back_populates='account')

# 16. FixedRateInvestment
# 16. FixedRateInvestment
class FixedRateInvestment(Base):
    __tablename__ = 'fixedrateinvestment'
    InvestID = Column(Integer, primary_key=True)
    AccID = Column(Integer, ForeignKey('bankaccount.AccID'), primary_key=True)
    Amount = Column(
        DECIMAL(15, 2),
        CheckConstraint("Amount > 0"),
        nullable=False
    )
    InterestRate = Column(
        DECIMAL(5, 2),
        CheckConstraint("InterestRate > 0 AND InterestRate <= 100"),
        nullable=False
    )
    StartDate = Column(Date, nullable=False)
    RiskLevel = Column(
        String(50),
        CheckConstraint("RiskLevel IN ('low', 'medium', 'high')")
    )
    Status = Column(
        String(50),
        CheckConstraint("Status IN ('active', 'matured', 'closed')"),
        nullable=False
    )
    MaturityDate = Column(Date, nullable=False)
    Type = Column(
        String(50),
        CheckConstraint("Type IN ('government bond', 'certificate of deposit', 'other')")
    )

    __table_args__ = (
        CheckConstraint('MaturityDate > StartDate', name='chk_maturity_after_start'),
    )

    account = relationship('BankAccount', back_populates='fixed_investments')


# 17. VariableRateInvestment
class VariableRateInvestment(Base):
    __tablename__ = 'variablerateinvestment'
    InvestID = Column(Integer, primary_key=True)
    AccID = Column(Integer, ForeignKey('bankaccount.AccID'), primary_key=True)
    Amount = Column(
        DECIMAL(15, 2),
        CheckConstraint("Amount > 0"),
        nullable=False
    )
    ReturnRate = Column(
        DECIMAL(5, 2),
        CheckConstraint("ReturnRate > 0 AND ReturnRate <= 100"),
        nullable=False
    )
    StartDate = Column(Date, nullable=False)
    RiskLevel = Column(
        String(50),
        CheckConstraint("RiskLevel IN ('low', 'medium', 'high')")
    )
    Status = Column(
        String(50),
        CheckConstraint("Status IN ('active', 'matured', 'closed')"),
        nullable=False
    )
    MaturityDate = Column(Date, nullable=False)
    Type = Column(
        String(50),
        CheckConstraint("Type IN ('bond', 'equity', 'other')")
    )
    InterestRate = Column(
        DECIMAL(5, 2),
        CheckConstraint("InterestRate > 0 AND InterestRate <= 100"),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint('MaturityDate > StartDate', name='chk_maturity_after_start'),
    )

    account = relationship('BankAccount', back_populates='variable_investments')

# 18. Transaction
class Transaction(Base):
    __tablename__ = 'transaction'
    TranID = Column(Integer, primary_key=True)
    AccID = Column(Integer, ForeignKey('bankaccount.AccID'), nullable=False)
    DestinationAccountID = Column(Integer, ForeignKey('bankaccount.AccID'))
    Type = Column(String(50), nullable=False)
    Amount = Column(DECIMAL(15, 2), nullable=False)
    Date = Column(Date, nullable=False)
    Status = Column(String(50), nullable=False)
    CurrencyType = Column(String(10), nullable=False)
    Method = Column(String(50), nullable=False)

    account = relationship('BankAccount', foreign_keys=[AccID], back_populates='transactions')
    destination_account = relationship('BankAccount', foreign_keys=[DestinationAccountID])

# 19. Access
class Access(Base):
    __tablename__ = 'access'
    Permission = Column(Integer, primary_key=True)
    Access = Column(String(100), nullable=False)

    rolepermissions = relationship('RolePermission', back_populates='access')

# 20. RolePermission
class RolePermission(Base):
    __tablename__ = 'rolepermission'
    RoleID = Column(Integer, ForeignKey('rolename.RoleID'), primary_key=True)
    Permission = Column(Integer, ForeignKey('access.Permission'), primary_key=True)

    role = relationship('RoleName', back_populates='rolepermissions')
    access = relationship('Access', back_populates='rolepermissions')

# 21. Loan
class Loan(Base):
    __tablename__ = 'loan'
    LoanID = Column(Integer, primary_key=True)
    Type = Column(String(50), nullable=False)
    Amount = Column(DECIMAL(15, 2), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)
    Status = Column(String(20), nullable=False)
    EmpID = Column(Integer, ForeignKey('employee.EmpID'))
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'))

    employee = relationship('Employee', back_populates='loans')
    customer = relationship('Customer', back_populates='loans')

# 22. LoanType
class LoanType(Base):
    __tablename__ = 'loantype'
    Type = Column(String(50), primary_key=True)
    InterestRate = Column(DECIMAL(5, 2), nullable=False)
    PaymentFrequency = Column(String(20), nullable=False)

# 23. Locker
class Locker(Base):
    __tablename__ = 'locker'
    LockerID = Column(Integer, primary_key=True)
    Location = Column(String(255), unique=True, nullable=False)
    SecurityType = Column(String(255), nullable=False)
    Size = Column(String(50))
    InstallationDate = Column(Date, nullable=False)
    LastAccessedDate = Column(Date)
    Status = Column(String(50), nullable=False)

    lockercustomers = relationship('LockerCustomer', back_populates='locker')
    lockerbranches = relationship('LockerBranch', back_populates='locker')

# 24. LockerCustomer
class LockerCustomer(Base):
    __tablename__ = 'lockercustomer'
    LockerID = Column(Integer, ForeignKey('locker.LockerID'), primary_key=True)
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'), primary_key=True)

    locker = relationship('Locker', back_populates='lockercustomers')
    customer = relationship('Customer', back_populates='lockercustomers')

# 25. LockerBranch
class LockerBranch(Base):
    __tablename__ = 'lockerbranch'
    LockerID = Column(Integer, ForeignKey('locker.LockerID'), primary_key=True)
    BranchID = Column(Integer, ForeignKey('branch.BranchID'), primary_key=True)

    locker = relationship('Locker', back_populates='lockerbranches')
    branch = relationship('Branch', back_populates='lockerbranches')

# 26. Assist
class Assist(Base):
    __tablename__ = 'assist'
    CustomerID = Column(Integer, ForeignKey('customer.CustomerID'), primary_key=True)
    EmpID = Column(Integer, ForeignKey('employee.EmpID'), primary_key=True)
    Date = Column(Date, primary_key=True)
    Time = Column(Time, primary_key=True)
    TypeOfInteraction = Column(String(300), nullable=False)

    customer = relationship('Customer', back_populates='assists')
    employee = relationship('Employee', back_populates='assists')

# Now, write functions to generate data for each table.

def generate_branches(n):
    branches = []
    statuses = ['Active', 'Inactive', 'Closed']
    for i in range(n):
        branch = Branch(
            BranchID=i+1,
            Name=fake.company(),
            Status=random.choice(statuses)
        )
        branches.append(branch)
    session.add_all(branches)
    session.commit()
    return branches

def generate_branch_addresses(branches):
    addresses = []
    for branch in branches:
        address = BranchAddress(
            Street=fake.street_address(),
            City=fake.city(),
            State=fake.state(),
            ZipCode=fake.zipcode(),
            Country=fake.country(),
            BranchID=branch.BranchID
        )
        addresses.append(address)
    session.add_all(addresses)
    session.commit()
    return addresses

def generate_branch_emails(branches):
    emails = []
    for branch in branches:
        email = BranchEmail(
            Email=fake.safe_email(),
            BranchID=branch.BranchID
        )
        emails.append(email)
    session.add_all(emails)
    session.commit()
    return emails

def generate_branch_phones(branches):
    phones = []
    for branch in branches:
        num_digits = random.randint(7, 15)
        phone_number = ''.join([str(random.randint(0, 9)) for _ in range(num_digits)])
        if random.choice([True, False]):
            phone_number = '+' + phone_number
        phones.append(BranchPhone(
            PhoneNumber=phone_number,
            BranchID=branch.BranchID
        ))
    session.add_all(phones)
    session.commit()
    return phones

def generate_role_names(n):
    roles = []
    for i in range(n):
        role = RoleName(
            RoleID=i+1,
            Name=fake.job()
        )
        roles.append(role)
    session.add_all(roles)
    session.commit()
    return roles

def generate_employees(n, roles):
    employees = []
    for i in range(n):
        role = random.choice(roles)
        employee = Employee(
            EmpID=i+1,
            Name=fake.name(),
            Street=fake.street_address(),
            City=fake.city(),
            State=fake.state(),
            ZipCode=fake.zipcode(),
            DateOfBirth=fake.date_of_birth(minimum_age=22, maximum_age=65),
            RoleID=role.RoleID,
            Gender=random.choice(['M', 'F'])
        )
        employees.append(employee)
    session.add_all(employees)
    session.commit()
    return employees

def generate_employee_emails(employees):
    emails = []
    for employee in employees:
        email = EmployeeEmail(
            EmpID=employee.EmpID,
            Email=fake.safe_email()
        )
        emails.append(email)
    session.add_all(emails)
    session.commit()
    return emails

def generate_employee_phones(employees):
    phones = []
    max_total_length = 15  # Maximum allowed length for PhoneNumber
    for employee in employees:
        add_plus = random.choice([True, False])
        if add_plus:
            num_digits = random.randint(7, max_total_length - 1)
            phone_number = '+' + ''.join([str(random.randint(0, 9)) for _ in range(num_digits)])
        else:
            num_digits = random.randint(7, max_total_length)
            phone_number = ''.join([str(random.randint(0, 9)) for _ in range(num_digits)])
        phones.append(EmployeePhone(
            EmpID=employee.EmpID,
            PhoneNumber=phone_number
        ))
    session.add_all(phones)
    session.commit()
    return phones


def generate_customers(n):
    customers = []
    for i in range(n):
        customer = Customer(
            CustomerID=i+1,
            Name=fake.name(),
            Street=fake.street_address(),
            City=fake.city(),
            State=fake.state(),
            ZipCode=fake.zipcode(),
            DateOfBirth=fake.date_of_birth(minimum_age=18, maximum_age=90),
            Gender=random.choice(['M', 'F'])
        )
        customers.append(customer)
    session.add_all(customers)
    session.commit()
    return customers

def generate_customer_emails(customers):
    emails = []
    for customer in customers:
        email = CustomerEmail(
            CustomerID=customer.CustomerID,
            Email=fake.safe_email()
        )
        emails.append(email)
    session.add_all(emails)
    session.commit()
    return emails

def generate_customer_phones(customers):
    phones = []
    max_total_length = 15  # Maximum allowed length for PhoneNumber
    for customer in customers:
        add_plus = random.choice([True, False])
        if add_plus:
            # Subtract 1 for the '+' sign
            num_digits = random.randint(7, max_total_length - 1)
            phone_number = '+' + ''.join([str(random.randint(0, 9)) for _ in range(num_digits)])
        else:
            num_digits = random.randint(7, max_total_length)
            phone_number = ''.join([str(random.randint(0, 9)) for _ in range(num_digits)])
        phones.append(CustomerPhone(
            CustomerID=customer.CustomerID,
            PhoneNumber=phone_number
        ))
    session.add_all(phones)
    session.commit()
    return phones


def generate_bank_accounts(customers, branches, n):
    accounts = []
    types = ['savings', 'checking', 'business']
    statuses = ['active', 'inactive', 'closed']
    for i in range(n):
        customer = random.choice(customers)
        branch = random.choice(branches)
        setup_date = fake.date_between(start_date='-5y', end_date='-1y')
        last_activity_date = fake.date_between(start_date=setup_date, end_date='today')
        account = BankAccount(
            AccID=i+1,
            Type=random.choice(types),
            SetupDate=setup_date,
            Balance=round(random.uniform(0, 100000), 2),
            Status=random.choice(statuses),
            BranchID=branch.BranchID,
            LastActivityDate=last_activity_date,
            CustomerID=customer.CustomerID
        )
        accounts.append(account)
    session.add_all(accounts)
    session.commit()
    return accounts

def generate_transactions(accounts, n):
    transactions = []
    types = ['deposit', 'withdrawal', 'transfer']
    statuses = ['completed', 'pending', 'failed']
    currencies = ['USD', 'EUR', 'AED', 'other']
    methods = ['bank transfer', 'cash', 'check', 'card', 'online']
    for i in range(n):
        account = random.choice(accounts)
        tran_type = random.choice(types)
        tran_date = fake.date_between(start_date=account.SetupDate, end_date='today')
        destination_account = random.choice(accounts) if tran_type == 'transfer' else None
        transaction = Transaction(
            TranID=i+1,
            AccID=account.AccID,
            DestinationAccountID=destination_account.AccID if destination_account else None,
            Type=tran_type,
            Amount=round(random.uniform(1, 10000), 2),
            Date=tran_date,
            Status=random.choice(statuses),
            CurrencyType=random.choice(currencies),
            Method=random.choice(methods)
        )
        transactions.append(transaction)
    session.add_all(transactions)
    session.commit()
    return transactions

def generate_loans(customers, employees, n):
    loans = []
    statuses = ['Active', 'Completed', 'Pending', 'Closed']
    for i in range(n):
        customer = random.choice(customers)
        employee = random.choice(employees)
        start_date = fake.date_between(start_date='-5y', end_date='-1y')
        end_date = fake.date_between(start_date=start_date, end_date='+5y')
        loan = Loan(
            LoanID=i+1,
            Type='Personal Loan',
            Amount=round(random.uniform(1000, 50000), 2),
            StartDate=start_date,
            EndDate=end_date,
            Status=random.choice(statuses),
            EmpID=employee.EmpID,
            CustomerID=customer.CustomerID
        )
        loans.append(loan)
    session.add_all(loans)
    session.commit()
    return loans

def generate_loan_types():
    loan_types = [
        LoanType(Type='Personal Loan', InterestRate=5.5, PaymentFrequency='Monthly'),
        LoanType(Type='Mortgage', InterestRate=3.5, PaymentFrequency='Monthly'),
        LoanType(Type='Auto Loan', InterestRate=4.0, PaymentFrequency='Monthly')
    ]
    session.add_all(loan_types)
    session.commit()
    return loan_types

def generate_access_permissions():
    permissions = [
        Access(Permission=1, Access='Read'),
        Access(Permission=2, Access='Write'),
        Access(Permission=3, Access='Update'),
        Access(Permission=4, Access='Delete')
    ]
    session.add_all(permissions)
    session.commit()
    return permissions

def generate_role_permissions(roles, permissions):
    role_permissions = []
    for role in roles:
        for permission in permissions:
            if random.choice([True, False]):
                role_permission = RolePermission(
                    RoleID=role.RoleID,
                    Permission=permission.Permission
                )
                role_permissions.append(role_permission)
    session.add_all(role_permissions)
    session.commit()
    return role_permissions

def generate_lockers(n):
    lockers = []
    security_types = ['electronic', 'key-based']
    sizes = ['small', 'medium', 'large']
    statuses = ['available', 'occupied', 'out of service']
    for i in range(n):
        installation_date = fake.date_between(start_date='-5y', end_date='-1y')
        last_accessed_date = fake.date_between(start_date=installation_date, end_date='today')
        locker = Locker(
            LockerID=i+1,
            Location=fake.address(),
            SecurityType=random.choice(security_types),
            Size=random.choice(sizes),
            InstallationDate=installation_date,
            LastAccessedDate=last_accessed_date if random.choice([True, False]) else None,
            Status=random.choice(statuses)
        )
        lockers.append(locker)
    session.add_all(lockers)
    session.commit()
    return lockers

def generate_locker_customers(lockers, customers):
    locker_customers = []
    for locker in lockers:
        if locker.Status == 'occupied':
            customer = random.choice(customers)
            locker_customer = LockerCustomer(
                LockerID=locker.LockerID,
                CustomerID=customer.CustomerID
            )
            locker_customers.append(locker_customer)
    session.add_all(locker_customers)
    session.commit()
    return locker_customers

def generate_locker_branches(lockers, branches):
    locker_branches = []
    for locker in lockers:
        branch = random.choice(branches)
        locker_branch = LockerBranch(
            LockerID=locker.LockerID,
            BranchID=branch.BranchID
        )
        locker_branches.append(locker_branch)
    session.add_all(locker_branches)
    session.commit()
    return locker_branches

def generate_assists(customers, employees, n):
    assists = []
    types_of_interaction = ['In-person', 'Phone Call', 'Email', 'Online Chat']
    for i in range(n):
        customer = random.choice(customers)
        employee = random.choice(employees)
        date = fake.date_between(start_date='-1y', end_date='today')
        time = fake.time()
        assist = Assist(
            CustomerID=customer.CustomerID,
            EmpID=employee.EmpID,
            Date=date,
            Time=time,
            TypeOfInteraction=random.choice(types_of_interaction)
        )
        assists.append(assist)
    session.add_all(assists)
    session.commit()
    return assists

def generate_customer_national_ids(customers):
    national_ids = []
    for customer in customers:
        national_id = CustomerNationalID(
            NationalID=fake.unique.bothify(text='???######'),  # Generates a random ID like 'ABC123456'
            CustomerID=customer.CustomerID
        )
        national_ids.append(national_id)
    session.add_all(national_ids)
    session.commit()
    return national_ids

def generate_employee_national_ids(employees):
    national_ids = []
    for employee in employees:
        national_id = EmployeeNationalID(
            NationalID=fake.unique.bothify(text='???######'),
            EmpID=employee.EmpID
        )
        national_ids.append(national_id)
    session.add_all(national_ids)
    session.commit()
    return national_ids

def generate_fixed_rate_investments(accounts, n):
    investments = []
    statuses = ['active', 'matured', 'closed']  # Allowed statuses
    types = ['government bond', 'certificate of deposit', 'other']  # Allowed types
    risk_levels = ['low', 'medium', 'high']  # Allowed risk levels
    for i in range(n):
        account = random.choice(accounts)
        invest_id = i + 1
        amount = round(random.uniform(0.01, 100000), 2)  # Amount > 0
        interest_rate = round(random.uniform(0.01, 100.00), 2)  # InterestRate > 0 and <= 100
        start_date = fake.date_between(start_date='-5y', end_date='-1y')
        # Ensure MaturityDate > StartDate
        maturity_date = fake.date_between(start_date=start_date + timedelta(days=1), end_date=start_date + timedelta(days=3650))
        investment = FixedRateInvestment(
            InvestID=invest_id,
            AccID=account.AccID,
            Amount=amount,
            InterestRate=interest_rate,
            StartDate=start_date,
            RiskLevel=random.choice(risk_levels),
            Status=random.choice(statuses),
            MaturityDate=maturity_date,
            Type=random.choice(types)
        )
        investments.append(investment)
    session.add_all(investments)
    session.commit()
    return investments

def generate_variable_rate_investments(accounts, n):
    investments = []
    statuses = ['active', 'matured', 'closed']  # Allowed statuses
    types = ['bond', 'equity', 'other']  # Allowed types as per schema
    risk_levels = ['low', 'medium', 'high']  # Allowed risk levels
    for i in range(n):
        account = random.choice(accounts)
        invest_id = i + 1
        amount = round(random.uniform(0.01, 100000), 2)  # Amount > 0
        return_rate = round(random.uniform(0.01, 100.00), 2)  # ReturnRate > 0 and <= 100
        interest_rate = round(random.uniform(0.01, 100.00), 2)  # InterestRate > 0 and <= 100
        start_date = fake.date_between(start_date='-5y', end_date='-1y')
        # Ensure MaturityDate > StartDate
        maturity_date = fake.date_between(
            start_date=start_date + timedelta(days=1),
            end_date=start_date + timedelta(days=3650)
        )
        investment = VariableRateInvestment(
            InvestID=invest_id,
            AccID=account.AccID,
            Amount=amount,
            ReturnRate=return_rate,
            StartDate=start_date,
            RiskLevel=random.choice(risk_levels),
            Status=random.choice(statuses),
            MaturityDate=maturity_date,
            Type=random.choice(types),
            InterestRate=interest_rate
        )
        investments.append(investment)
    session.add_all(investments)
    session.commit()
    return investments

def generate_role_statuses(roles):
    statuses = []
    status_options = ['Active', 'Inactive', 'Pending']
    for role in roles:
        role_status = RoleStatus(
            Name=role.Name,
            Status=random.choice(status_options),
            RoleDescription=fake.text(max_nb_chars=200)
        )
        statuses.append(role_status)
    session.add_all(statuses)
    session.commit()
    return statuses


# Main function to generate and insert data

def main():
    # Create all tables
    Base.metadata.create_all(engine)

    # Generate data
    print("Generating branches...")
    # branches = generate_branches(5)
    # generate_branch_addresses(branches)
    # generate_branch_emails(branches)
    # generate_branch_phones(branches)
    branches = session.query(Branch).all()

    print("Generating roles...")
    # roles = generate_role_names(5)
    roles = session.query(RoleName).all()

    print("Generating role statuses...")
    # generate_role_statuses(roles)

    print("Generating employees...")
    # employees = generate_employees(10, roles)
    # generate_employee_emails(employees)
    # generate_employee_phones(employees)
    employees = session.query(Employee).all()

    # Generate employee national IDs
    print("Generating employee national IDs...")
    # generate_employee_national_ids(employees)

    print("Generating customers...")
    # Comment out the following line if customers are already generated
    # customers = generate_customers(50)
    customers = session.query(Customer).all()
    # generate_customer_emails(customers)
    # generate_customer_phones(customers)

    print("Generating customer national IDs...")
    # generate_customer_national_ids(customers)

    print("Generating bank accounts...")
    # accounts = generate_bank_accounts(customers, branches, 100)
    accounts = session.query(BankAccount).all()

    print("Generating fixed rate investments...")
    # generate_fixed_rate_investments(accounts, 50)

    print("Generating variable rate investments...")
    generate_variable_rate_investments(accounts, 50)

    print("Generating transactions...")
    # generate_transactions(accounts, 200)
    transactions = session.query(Transaction).all()

    print("Generating loans...")
    # generate_loan_types()
    # generate_loans(customers, employees, 20)
    loans = session.query(Loan).all()

    print("Generating access permissions...")
    # permissions = generate_access_permissions()
    permissions = session.query(RolePermission).all()
    # generate_role_permissions(roles, permissions)


    print("Generating lockers...")
    # lockers = generate_lockers(10)
    lockers = session.query(Locker).all()
    # generate_locker_customers(lockers, customers)
    # generate_locker_branches(lockers, branches)

    print("Generating assists...")
    # generate_assists(customers, employees, 30)

    print("Sample data generation completed.")

if __name__ == "__main__":
    main()
    session.close()
