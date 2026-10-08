import time
import requests

print("=== PASO 1: Países con GraphQL (10 países en 1 petición) ===")
query_paises = """
{
  countries(filter: {code: {in: ["MX", "AR", "BR", "CO", "PE", "CL", "ES", "US", "CA", "JP"]}}) {
    name
    capital
    currency
  }
}
"""
t = time.perf_counter()
r_paises = requests.post(
    "https://countries.trevorblades.com/",
    json={"query": query_paises},
    timeout=10
)
ms_paises = (time.perf_counter() - t) * 1000
print(f"Código: {r_paises.status_code} | Tiempo: {ms_paises:.0f} ms | Bytes: {len(r_paises.content)}")
print("Respuesta parcial países:", r_paises.json().get("data", {}).get("countries", [])[:2]) # Muestra los primeros 2 para verificar
print("-" * 60)


print("=== PASO 2.1: Pokémon con REST (10 peticiones individuales) ===")
nombres_pokemon = [
    "pikachu", "bulbasaur", "charmander", "squirtle", "eevee",
    "snorlax", "gengar", "onix", "psyduck", "jigglypuff"
]
total_bytes_rest = 0
t_start = time.perf_counter()

for n in nombres_pokemon:
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{n}", timeout=10)
    total_bytes_rest += len(r.content)

ms_rest = (time.perf_counter() - t_start) * 1000
print(f"REST -> Peticiones: {len(nombres_pokemon)} | Total Bytes: {total_bytes_rest} | Tiempo total: {ms_rest:.0f} ms")
print("-" * 60)


print("=== PASO 2.2: Pokémon con GraphQL (1 sola petición) ===")
# Nota: La estructura exacta para la beta de GraphQL de PokéAPI suele requerir la lista o el filtro por nombre.
# Si la API de GraphQL de PokéAPI llega a requerir una sintaxis específica por los nombres, 
# usaremos la consulta adaptada a su esquema actual:
query_pokemon = """
{
  pokemon_v2_pokemon(where: {name: {_in: ["pikachu", "bulbasaur", "charmander", "squirtle", "eevee", "snorlax", "gengar", "onix", "psyduck", "jigglypuff"]}}) {
    name
    height
    pokemon_v2_pokemontypes {
      pokemon_v2_type {
        name
      }
    }
  }
}
"""

t = time.perf_counter()
r_gql = requests.post(
    "https://beta.pokeapi.co/graphql/v1beta", # Endpoint oficial actual de la v1beta2/beta de pokeapi graphql
    json={"query": query_pokemon},
    timeout=15
)
ms_gql = (time.perf_counter() - t) * 1000
print(f"Código GraphQL: {r_gql.status_code}")
print(f"GraphQL -> Peticiones: 1 | Total Bytes: {len(r_gql.content)} | Tiempo total: {ms_gql:.0f} ms")
if r_gql.status_code == 200:
    print("Respuesta GraphQL:", r_gql.json())
else:
    print("Error o respuesta:", r_gql.text)