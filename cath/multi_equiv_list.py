class multi_equiv_list:
	
	def __init__(self, num_entries: int):
		if not num_entries:
			raise Exception("Cannot build a multi_equiv_list with 0 entries")
		self.m_num_entries = num_entries

	def num_entries(self):
		return self.m_num_entries
