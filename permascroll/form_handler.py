"""
"""

class TestForm(gappforms.Modelform):
	class Meta:
		model = Feed
		fields = ['index']
