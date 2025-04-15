import random
import re
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
import scipy.stats as stats
from scipy.stats import bootstrap
import statistics as st
import numpy as np
from collections import Counter


def open_file(fn):
	with open(fn, "r") as f:
		lines = f.readlines()
	return lines


def replace_from_dict(string, replacements):
	for old, new in replacements.items():
		string = string.replace(old, new)
	return string


def get_user_string(how, seed):
	random.seed(seed)
	random_int = str(random.randint(100, 10000))

	if how == "user":
		person_str = "user"
	elif how == "person":
		person_str = "person"

	user_id = f"{person_str}{random_int}"
	return user_id


def make_aesthetic(hex_color_list=None,
				   with_gridlines=False,
				   bold_title=False,
				   save_transparent=False,
				   font_scale=2,
				   latex2arial=True
				   ):
	"""Make Seaborn look clean and add space between title and plot"""

	# Note: To make some parts of title bold and others not bold, we have to use
	# latex rendering. This should work:
	# plt.title(r'$\mathbf{bolded\ title}$' + '\n' + 'And a non-bold subtitle')

	sns.set(style='white', context='paper', font_scale=font_scale)
	if not hex_color_list:
		# 2024-11-28: Reordered color list
		hex_color_list = [
			"#2C3531",  # Dark charcoal gray with green undertone
			"#D41876",  # Telemagenta
			"#00A896",  # Persian green
			"#826AED",  # Medium slate blue
			"#F45B69",  # Vibrant pinkish-red
			"#E3B505",  # Saffron
			"#89DAFF",  # Pale azure
			"#342E37",  # Dark grayish-purple
			"#7DCD85",  # Emerald
			"#F7B2AD",  # Melon
			"#D4B2D8",  # Pink lavender
			"#020887",  # Phthalo blue
			"#E87461",  # Medium-bright orange
			"#7E6551",  # Coyote
			"#F18805"  # Tangerine
		]

	sns.set_palette(sns.color_palette(hex_color_list))

	# Update on
	# 2024-11-29: I realized I can automatically
	# clean variable names so i dont have to manually replace underscore

	# Enhanced typography settings
	plt.rcParams.update({
		# font settings
		'font.family': 'Arial',
		'font.weight': 'regular',
		'axes.labelsize': 11 * font_scale,
		'axes.titlesize': 14 * font_scale,
		'xtick.labelsize': 10 * font_scale,
		'ytick.labelsize': 10 * font_scale,
		'legend.fontsize': 10 * font_scale,

		# spines/grids
		'axes.spines.right': False,
		'axes.spines.top': False,
		'axes.spines.left': True,
		'axes.spines.bottom': True,
		'axes.linewidth': 0.8,  # Thinner spines
		'axes.grid': with_gridlines,
		'grid.alpha': 0.2,
		'grid.linestyle': ':',
		'grid.linewidth': 0.5,

		# title
		'axes.titlelocation': 'left',
		'axes.titleweight': 'bold' if bold_title else 'regular',
		'axes.titlepad': 15 * (font_scale / 1),

		# fig
		'figure.facecolor': 'white',
		'axes.facecolor': 'white',
		'figure.constrained_layout.use': True,
		'figure.constrained_layout.h_pad': 0.2,
		'figure.constrained_layout.w_pad': 0.2,

		# legend
		'legend.frameon': True,
		'legend.framealpha': 0.95,
		'legend.facecolor': 'white',
		'legend.borderpad': 0.4,
		'legend.borderaxespad': 1.0,
		'legend.handlelength': 1.5,
		'legend.handleheight': 0.7,
		'legend.handletextpad': 0.5,

		# export
		'savefig.dpi': 300,
		'savefig.transparent': save_transparent,
		'savefig.bbox': 'tight',
		'savefig.pad_inches': 0.2,
		'figure.autolayout': False,

		# do this for the bold hack
		'mathtext.fontset': 'custom',
		'mathtext.rm': 'Arial',
		'mathtext.it': 'Arial:italic',
		'mathtext.bf': 'Arial:bold'

	})

	return hex_color_list


def clean_vars(s, how='title'):
	"""
	Simple function to clean titles

	Params
	- s: The string to clean
	- how (default='title'): How to return string. Can be either ['title', 'lowercase', 'uppercase']

	Returns
	- cleaned string
	"""
	assert how in ['title', 'lowercase', 'uppercase'], "Bad option!! see docs"
	s = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s)
	s = s.replace('_', ' ')
	if how == 'title':
		return s.title()
	elif how == 'lower':
		return s.lower()
	elif how == 'upper':
		return s.upper()


def categorical_stats(data, include_n=True, digits=1, sort_by='frequency', reverse=True):
	"""
	Calculate and format statistics for categorical data.

	Parameters:
	-----------
	data : array-like
		The input categorical data array
	include_n : bool, optional
		Whether to include raw counts in the output (default: True)
	digits : int, optional
		Number of decimal places for percentage rounding (default: 1)
	sort_by : str, optional
		How to sort the results: 'frequency' (default), 'alphabetical', or 'original'
	reverse : bool, optional
		Whether to reverse the sort order (default: True for descending frequency)

	Returns:
	--------
	str
		Formatted string showing categories with percentages and optionally counts
	dict
		Dictionary containing the calculated statistics for programmatic use
	"""

	# Convert to numpy array for consistency
	data = np.array(data)

	# Count frequencies
	counter = Counter(data)
	total_count = len(data)

	# Calculate percentages and build results dictionary
	result_dict = {}
	for category, count in counter.items():
		percentage = (count / total_count) * 100
		result_dict[category] = {
			'count': count,
			'percentage': percentage,
			'percentage_rounded': round(percentage, digits)
		}

	# Sort results according to preference
	if sort_by == 'frequency':
		sorted_items = sorted(result_dict.items(),
							  key=lambda x: x[1]['count'],
							  reverse=reverse)
	elif sort_by == 'alphabetical':
		sorted_items = sorted(result_dict.items(),
							  key=lambda x: str(x[0]),
							  reverse=reverse)
	elif sort_by == 'original':
		# Maintain order of first appearance in the data
		seen = set()
		original_order = []
		for item in data:
			if item not in seen:
				seen.add(item)
				original_order.append(item)
		sorted_items = [(item, result_dict[item]) for item in original_order]
	else:
		raise ValueError("sort_by must be 'frequency', 'alphabetical', or 'original'")

	# Format output string
	result_parts = []
	for category, stats in sorted_items:
		if include_n:
			part = f"{category} ({stats['percentage_rounded']:.{digits}f}%; n={stats['count']})"
		else:
			part = f"{category} ({stats['percentage_rounded']:.{digits}f}%)"
		result_parts.append(part)

	result_string = ", ".join(result_parts)

	# Return both the formatted string and the full dictionary for programmatic use
	return result_string, {k: v for k, v in sorted_items}


def array_stats(data, digits=2, include_ci=False):
	"""
	Calculate and print summary statistics for an array.

	Parameters:
	-----------
	data : array-like
		The input data array
	digits : int, optional
		Number of decimal places for rounding (default: 2)
	include_ci : bool, optional
		Whether to include confidence interval (default: False)

	Returns:
	--------
	dict
		Dictionary containing the calculated statistics
	"""
	data = np.array(data)

	mean_val = np.mean(data)
	median_val = np.median(data)
	sd_val = np.std(data, ddof=1)

	# Calculate mode - handling cases with multiple modes
	try:
		mode_val = st.mode(data)
	except st.StatisticsError:
		# If multiple modes exist, use scipy's mode which returns the first occurrence
		print("Multiple modes found, using the first one.")
		mode_val = stats.mode(data, keepdims=True)[0][0]

	result = {
		'mean': round(mean_val, digits),
		'median': round(median_val, digits),
		'sd': round(sd_val, digits),
		'mode': round(mode_val, digits)
	}

	# Add confidence interval if requested
	if include_ci:
		def mean_func(x, axis):
			return np.mean(x, axis=axis)

		data_reshaped = np.array(data).reshape(-1, 1)

		bootstrap_result = bootstrap((data_reshaped,), mean_func,
									 confidence_level=0.95,
									 random_state=42,
									 n_resamples=10 * 1000)

		ci_lower, ci_upper = bootstrap_result.confidence_interval
		result['ci'] = (round(float(ci_lower), digits), round(float(ci_upper), digits))

	print(f"M = {result['mean']:.{digits}f}, SD = {result['sd']:.{digits}f}, Mdn = {result['median']:.{digits}f}")
	print(f"Mode = {result['mode']:.{digits}f}")

	if include_ci and 'ci' in result:
		print(f"95% CI [{result['ci'][0]:.{digits}f}, {result['ci'][1]:.{digits}f}]")

	return result


def pymer2latex(model, caption=None, label=None, include_random=True, write_to_file=None):
	"""
	Create a LaTeX table from pymer4 model results.

	Basically, Stargazer in Python is how one normally reports regressions in a pretty way but Stargazer
	does not support pymer4 (afaik), so this is a very crude workaround.

	Args:
		model: A fitted pymer4.models object to summarize.
		caption: Optional string for the LaTeX table caption.
		label: Optional string for the LaTeX table label (for cross-referencing).
		include_random: Boolean indicating whether to include random effects.
		write_to_file: Optional string path to save the LaTeX code to a file.

	Returns:
		str: LaTeX code for the table.
	"""

	# 1. HEADER STUFF
	###################
	latex = "\\begin{table}[htbp]\n\\centering\n"
	if caption:
		latex += f"\\caption{{{caption}}}\n"
	if label:
		latex += f"\\label{{{label}}}\n"
	latex += "\\begin{tabular}{lcccc}\n\\hline\n"
	latex += " & Estimate & SE & t-value & p-value \\\\ \n\\hline\n"

	# 2. FIXED FX
	###################
	for idx, row in model.coefs.iterrows():
		param_name = "Intercept" if idx == "(Intercept)" else idx
		stars = ""
		if row['P-val'] < 0.001:
			stars = "$^{***}$"
		elif row['P-val'] < 0.01:
			stars = "$^{**}$"
		elif row['P-val'] < 0.05:
			stars = "$^{*}$"
		p_val = f"${row['P-val']:.2e}$" if row['P-val'] < 0.01 else f"{row['P-val']:.4f}"
		latex += f"{param_name} & {row['Estimate']:.3f}{stars} & {row['SE']:.3f} & {row['T-stat']:.3f} & {p_val} \\\\ \n"

	# 3. RANDOM FX
	###################
	if include_random and hasattr(model, 'ranef_var'):
		latex += "\\hline\n\\multicolumn{5}{l}{\\textit{Random Effects}} \\\\ \n\\hline\n"
		latex += "Group & Parameter & Variance & Std.Dev & \\\\ \n"

		for idx, row in model.ranef_var.iterrows():
			if idx == 'Residual':
				group, param = 'Residual', ''
			elif '_' in idx:
				parts = idx.split('_')
				group, param = parts[0], 'Intercept' if len(parts) == 1 else parts[1]
			else:
				group, param = idx, 'Intercept'

			latex += f"{group} & {param} & {row['Var']:.3f} & {row['Std']:.3f} & \\\\ \n"

	# 4. SUMMARY STATS
	####################
	latex += "\\hline\n"
	latex += f"\\multicolumn{{5}}{{l}}{{Observations: {len(model.data)}}} \\\\ \n"

	if hasattr(model, 'AIC'):
		latex += f"\\multicolumn{{5}}{{l}}{{AIC: {model.AIC:.1f}}} \\\\ \n"

	# 5. GROUP INFO
	####################
	if hasattr(model, 'grps') and model.grps:
		grp_info = "; ".join([f"{name}: {size}" for name, size in model.grps.items()])
		latex += f"\\multicolumn{{5}}{{l}}{{Groups: {grp_info}}} \\\\ \n"

	# 6. NOTE ABOUT SIG
	####################
	latex += "\\hline\n"
	latex += "\\multicolumn{5}{l}{\\textit{Note:} $^{*}p<0.05$; $^{**}p<0.01$; $^{***}p<0.001$} \\\\ \n"
	latex += "\\hline\n\\end{tabular}\n\\end{table}"

	# Write to file if path is provided
	if write_to_file:
		with open(write_to_file, 'w') as f:
			f.write(latex)

	return latex
