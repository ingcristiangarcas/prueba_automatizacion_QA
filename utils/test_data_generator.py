import random
from faker import Faker

# Inicializamos Faker. 
# Usamos 'es_CO' para que genere datos con formato colombiano (nombres, etc.)
fake = Faker('es_CO') 

def generate_passenger_data():
    """
    Genera datos aleatorios para UN pasajero.
    (Utilizado principalmente para el Caso 1)
    """
    # --- LÓGICA DE GÉNERO AÑADIDA ---
    gender = random.choice(['Masculino', 'Femenino'])
    first_name = fake.first_name_male() if gender == 'Masculino' else fake.first_name_female()
    # ---
    
    return {
        'first_name': first_name,
        'last_name': fake.last_name(),
        'gender': gender, # <-- ¡AÑADIDO!
        'dob': fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%d/%m/%Y'),
        'email': fake.email(),
        'phone': f"315{fake.random_number(digits=7, fix_len=True)}", 
        'doc_type': 'Documento de identidad', 
        'doc_number': fake.numerify(text='##########')
    }

def generate_passenger_data_for_roundtrip(num_passengers):
    """
    Genera una lista de pasajeros para el Caso 2 (Round-trip).
    - Pasajero 1 debe ser 'Test Test' (Masculino por defecto).
    - Usa diferentes tipos de documento y géneros.
    """
    passengers = []
    
    doc_types = [
        "Documento de identidad", 
        "Pasaporte", 
        "Cédula de Extranjería", 
        "Pasaporte diplomático"
    ] 

    for i in range(num_passengers):
        # --- LÓGICA DE GÉNERO AÑADIDA ---
        gender = random.choice(['Masculino', 'Femenino'])
        
        if i == 0:
            first_name = 'Test'
            last_name = 'Test'
            gender = 'Masculino' # Forzamos a 'Test Test' a ser Masculino
        else:
            if gender == 'Femenino':
                first_name = fake.first_name_female()
            else:
                first_name = fake.first_name_male()
            last_name = fake.last_name()
        # --- FIN LÓGICA GÉNERO ---
        
        doc_type = doc_types[i % len(doc_types)]
        
        passenger = {
            'first_name': first_name,
            'last_name': last_name,
            'gender': gender, # <-- ¡AÑADIDO!
            'doc_type': doc_type,
            'doc_number': fake.numerify(text='##########'),
            'dob': fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%d/%m/%Y'),
            'email': fake.email(),
            'phone': f"315{fake.random_number(digits=7, fix_len=True)}"
        }
        passengers.append(passenger)
        
    return passengers

def generate_credit_card_info():
    """
    Genera datos de tarjeta de crédito FAKE para el pago (Caso 1).
    """
    return {
        'card_number': '4000000000000002', 
        'card_holder': fake.name(),
        'expiry_month': str(random.randint(1, 12)).zfill(2), # Formato MM
        'expiry_year': str(random.randint(2028, 2035)), # Formato YYYY
        'cvv': str(random.randint(100, 999))
    }