from flask import Flask
import os
import pexpect

app = Flask(__name__)


# Route to call to create settlement request, confirm settlement, and transfer product between two users
@app.route('/')
def settle_and_transfer(from_address, to_address, settlement_amount):
    # Get CWD for going back later
    cwd = os.getcwd()

    # Change the path so that we can call the settlement jar
    os.chdir('/Users/patrickarchambeau/Projects/java-blockchain-barebones-settlementapp/target')

    # Create Settlement Request and Confirm Settlement calling Jar
    child = pexpect.spawn('./barebones_settlement_java.sh')

    # Create Settlement Request
    child.expect('Key')
    child.sendline('\n')
    child.expect('Keystore Password')
    child.sendline('\n')
    child.expect('Consumer Key')
    child.sendline('\n')
    child.expect('Key Alias')
    child.sendline('\n')
    child.expect('Protocol Definition Path')
    child.sendline('\n')
    child.expect('App Id')
    child.sendline('TM03\n')
    child.expect('press return ')
    child.sendline('\n')
    child.expect('Option ')
    child.sendline('3\n')
    child.expect('from')
    # SETTLEMENT FROM ADDRESS (John User 1)
    child.sendline(from_address + '\n')
    child.expect('to')
    # SETTLEMENT TO ADDRESS (Jane User 2)
    child.sendline(to_address + '\n')
    child.expect('amount_minor_units')
    child.sendline(settlement_amount + '\n')
    child.expect('currency')
    # USD default
    child.sendline('\n')
    child.expect('description')
    child.sendline('Creating Settlement payment from John to Jane\n')

    # Stop here so we can try to grab the Hash value
    child.expect('Slot:')

    # Grab the value of the hash coming back
    child_before = child.before

    settlement_hash = child_before.split("Hash: ", 1)[1]

    child.expect('pending')
    child.sendline('\n')
    # Settlement Request from John to Jane has been created

    # Confirm Settlement
    child.expect('Option ')
    child.sendline('4\n')
    child.expect('hash')
    # Use the settlement has from the newly created settlement
    child.sendline(settlement_hash + '\n')
    child.expect('encoding')
    child.sendline('\n')
    child.expect('press return ')
    child.sendline('\n')

    # Public Key and Signature have been created at this point

    # MOVING TO PROVENANCE TO INITIATE PRODUCT TRANSFER
    # Change Directories to run provenance shell script
    os.chdir('/Users/patrickarchambeau/Projects/java-provenance-barebones-client/target')

    # TRANSFER THE PRODUCT FROM JOHN TO JANE
    child = pexpect.spawn('./barebones_provenance_java.sh')
    child.expect('Key')
    child.sendline('\n')
    child.expect('Keystore Password')
    child.sendline('\n')
    child.expect('Consumer Key')
    child.sendline('\n')
    child.expect('Key Alias')
    child.sendline('\n')
    child.expect('Team Name')
    child.sendline('TM03\n')
    child.expect('Protocol')
    child.sendline('\n')
    child.expect('Option ')
    child.sendline('6\n')
    child.expect('Select')
    # One product "Photoshop"
    child.sendline('1\n')
    child.expect('Select')
    # Select Jane Smith (Make sure before DEMO ownership of photoshop is on John Doe)
    child.sendline('2\n')
    child.expect('Photoshop transferred')

    # Grab the value of the final transfer hash coming back
    child_before = child.before
    final_transfer_hash = child_before.split("Hash: ", 1)[1]

    # Change back to python path
    os.chdir(cwd)

    # RETURN TOKEN TRANSFER HASH #
    return final_transfer_hash


if __name__ == '__main__':
    app.run()
