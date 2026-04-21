import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core/logic')))
import network

def test_port_logic():
    # Encontrar un puerto libre
    free_port = network.find_free_port(9000)
    print(f"Found free port: {free_port}")
    assert not network.is_port_in_use(free_port)
    
    # Simular ocupación (esto es difícil sin levantar un server real, 
    # pero podemos probar que la función no explota)
    assert isinstance(network.is_port_in_use(80), bool)
    print("Network logic basic tests passed!")

if __name__ == '__main__':
    test_port_logic()
