from paystackapi.paystack import Paystack
paystack_secret_key = "sk_test_faadf90960bad25e6a2b5c9be940792f928b73ac"
paystack = Paystack(secret_key=paystack_secret_key)

# to use transaction class
paystack.transaction.list()

# to use customer class
# paystack.customer.get(transaction_id)

# to use plan class
# paystack.plan.get(plan_id)

# to use subscription class
paystack.subscription.list()
