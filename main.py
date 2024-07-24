from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PayParams,
    AssetFreezeParams,

)

# Client to connect to localnet
algorand = AlgorandClient.default_local_net()

# Import dispenser from KMD 
dispenser = algorand.account.dispenser()
print("Dispenser Address: ", dispenser.address)

# Create a wallet for the creator of the token
creator = algorand.account.random()
print("Creator Address: ",creator.address)

# Get account info about creator
print(algorand.account.get_information(creator.address))

# Fund creator address with algo
algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=creator.address,
        amount=10_000_000
    )
)

# Check out the creator account changes after funding
print(algorand.account.get_information(creator.address))

# Create Algorand Standard Asset
sent_txn = algorand.send.asset_create(
    AssetCreateParams(
        sender=creator.address,
        total= 1000,
        asset_name="nameofasset",
        unit_name="NOA",
        manager=creator.address,
        clawback=creator.address,
        freeze=creator.address
    )
)

# Extracting the confirmation and asset index of the asset creation transaction to get asset ID
asset_id= sent_txn["confirmation"]["asset-index"]
print("Asset ID: ", asset_id)

# Create receiver account
receiver_acct = algorand.account.random()
print("Receiver Account: ", receiver_acct.address)

# Fund receiver account
algorand.send.payment(
    PayParams(
        sender=dispenser.address,
        receiver=receiver_acct.address,
        amount=10_000_000
    )
)

print(algorand.account.get_information(receiver_acct.address))

# showcase error whithout opt-in

'''
asset_transfer = algorand.send.asset_transfer(
    AssetTransferParams(
        sender=creator.address,
        receiver=receiver_acct.address,
        asset_id=asset_id,
        amount=10
    )
) 
'''

#----------------------------------------------------------
# Opt-in segment without atomic transfer

# 1 Fund receiver account
# algorand.send.payment(
#     PayParams(
#         sender=dispenser.address,
#         receiver=receiver_acct.address,
#         amount=10_000_000
#     )
# )


# 2 Optin to the asset 
# algorand.send.asset_opt_in(
#     AssetOptInParams(
#         sender=receiver_acct.address,
#         asset_id=asset_id
#     )
# )

# 3 Transfer the asset (Code above)
# ---------------------------------------------------------

# Atomic transfer segment - optin txn / payment txn / asset transfer txn

# Create a new transaction group
group_tx = algorand.new_group()

# Add an asset opt-in transaction to the group
group_tx.add_asset_opt_in(
    AssetOptInParams(
        sender=receiver_acct.address,  
        asset_id=asset_id               
    )
)

# Add a payment transaction to the group
group_tx.add_payment(
    PayParams(
        sender=receiver_acct.address,   
        receiver=creator.address,       
        amount=1_000_000                
    ))

# Add an asset transfer transaction to the group
group_tx.add_asset_transfer(
    AssetTransferParams(
        sender=creator.address,         
        receiver=receiver_acct.address, 
        asset_id=asset_id,              
        amount=10                       
    )
)

# Execute the transaction group
group_tx.execute()

# Print the entire information from the Receiver Account
print(algorand.account.get_information(receiver_acct.address))

# Print the amount of the asset the receiver account holds after the transactions
print("Receiver Account Asset Balance:",algorand.account.get_information(receiver_acct.address)['assets'][0]['amount'])

# Print the remaining balance of the creator account after the transactions
print("Creator Account Balance:", algorand.account.get_information(creator.address)['amount'])

#-------------------------------------------------------
# Challenges
# Freeze

algorand.send.asset_freeze(
    AssetFreezeParams(
        sender=creator.address,
        asset_id=asset_id,
        account=receiver_acct.address,
        frozen= True
    )
)

# Test freeze error
""" algorand.send.asset_transfer(
    AssetTransferParams(
            sender=receiver_acct.address,
            receiver=creator.address,
            asset_id=asset_id,
            amount=2
        )
)
 """

# UnFreeze

algorand.send.asset_freeze(
    AssetFreezeParams(
        sender=creator.address,
        asset_id=asset_id,
        account=receiver_acct.address,
        frozen= False
    )
)

# Send asset

algorand.send.asset_transfer(
    AssetTransferParams(
            sender=receiver_acct.address,
            receiver=creator.address,
            asset_id=asset_id,
            amount=2
        )
)


print(algorand.account.get_information(receiver_acct.address)['assets'][0]['amount'])

# Clawback

algorand.send.asset_transfer(
    AssetTransferParams(
            sender= creator.address,
            receiver= creator.address,
            asset_id=asset_id,
            amount=2,
            clawback_target= receiver_acct.address
        )
)

print(algorand.account.get_information(receiver_acct.address)['assets'][0]['amount'])
