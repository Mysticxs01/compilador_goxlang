# symtab.py
from rich.table   import Table
from rich.console import Console
from rich         import print

class Symtab:
	'''
	Una tabla de símbolos.  Este es un objeto simple que sólo
	mantiene una hashtable (dict) de nombres de simbolos y los
	nodos de declaracion o definición de funciones a los que se
	refieren.
	Hay una tabla de simbolos separada para cada elemento de
	código que tiene su propio contexto (por ejemplo cada función,
	clase, tendra su propia tabla de simbolos). Como resultado,
	las tablas de simbolos se pueden anidar si los elementos de
	código estan anidados y las búsquedas de las tablas de
	simbolos se repetirán hacia arriba a través de los padres
	para representar las reglas de alcance léxico.
	'''
	class SymbolDefinedError(Exception):
		'''
		Se genera una excepción cuando el código intenta agregar
		un simbol a una tabla donde el simbol ya se ha definido.
		Tenga en cuenta que 'definido' se usa aquí en el sentido
		del lenguaje C, es decir, 'se ha asignado espacio para el
		simbol', en lugar de una declaración.
		'''
		pass
		
	class SymbolConflictError(Exception):
		'''
		Se produce una excepción cuando el código intenta agregar
		un símbolo a una tabla donde el símbolo ya existe y su tipo
		difiere del existente previamente.
		'''
		pass
		
	def __init__(self, name, parent=None, scope_type="global"):
		'''
		Crea una tabla de símbolos vacia con la tabla de
		simbolos padre dada.
		'''
		self.name = name
		self.entries = {}
		self.parent = parent
		self.scope_type = scope_type
		if self.parent:
			self.parent.children.append(self)
		self.children = []
	
	def find_scope_of_type(self, scope_type):
		env = self
		while env:
			if env.scope_type == scope_type:
				return env
			env = env.parent
		return None
	
	def find_scope_of_type_name_child(self, scope_type, name):
		# Busca también en el env actual
		if self.scope_type == scope_type and self.entries.get(name):
			return self
		for child in self.children:
			if child.scope_type == scope_type and child.entries.get(name):
				return child
		return None
	
	def add(self, name, value):
		'''
		Agrega un simbol con el valor dado a la tabla de simbolos.
		El valor suele ser un nodo AST que representa la declaración
		o definición de una función, variable (por ejemplo, Declaración
		o FuncDeclaration)
		'''
		if name in self.entries:
			if self.entries[name].dtype != value.dtype:
				raise Symtab.SymbolConflictError(f"Conflicto: '{name}' tiene tipo diferente.")
			else:
				raise Symtab.SymbolDefinedError(f"Redefinición: '{name}' ya fue definido.")
		self.entries[name] = value

	#Agrega un método para quitar del env, como el inverso de add
	def remove(self, name):
		if name in self.entries:
			del self.entries[name]
		else:
			raise Symtab.SymbolNotFoundError(f"No se encontró: '{name}'")
		

	def get(self, name):
		'''
		Recupera el símbol con el nombre dado de la tabla de
		simbol, recorriendo hacia arriba a traves de las tablas
		de simbol principales si no se encuentra en la actual.
		'''
		if name in self.entries:
			return self.entries[name]
		elif self.parent:
			return self.parent.get(name)
		return None
		
	def print(self):
		table = Table(title = f"Symbol Table: '{self.name}'")
		table.add_column('key', style='cyan')
		table.add_column('value', style='bright_green')
		
		for k, v in self.entries.items():
			if hasattr(v, 'name'):
				value = f"{v.__class__.__name__}({v.name})"
			else:
				value = f"{v.__class__.__name__}({v})"
			table.add_row(k, value)
		print(table, '\n')
		
		for child in self.children:
			child.print()

