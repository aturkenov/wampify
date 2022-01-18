# SQL Alchemy usage example

I use sqlalchemy (dml) operators because:
1. Alchemy is maximally similar to sql
2. It's flexible
3. And it's good implementation ;)

## SessionFactory (SF) (session_factory.py)
You can connect it to Wampify session pool according to your needs (more about Session Factory)

## Base Provider (BaseAlchemyProvider) (provider.py)
(more about providers)

## Base Model Provider (BaseAlchemyModelProvider) (provider.py)
I think, Provider (more about providers) could not be universal for everyone, so BaseAlchemyModelProvider is general implementation of realy required methods. You need to declare beginning of select statement, also for update, delete, insert and their returning.

### Filtering - Filters for statements
AlchemyFIlters contain most useful lookup fields (in django like style (sent_time__ge) to simple filtering. Just declare your columns to filter and if you need, you can add your lookup operators