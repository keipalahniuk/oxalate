from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponse, JsonResponse

from .models import Ingredient, Meal, MealIngredient

# Create your views here.
def lookup(request):
	if 'term' in request.GET:
		qsMeal = Meal.objects.filter(name__icontains=request.GET.get('term'))
		qsIngredient = Ingredient.objects.filter(name__icontains=request.GET.get('term'))
		names = list()
		for meal in qsMeal:
			names.append("m/"+meal.name)
		for ingredient in qsIngredient:
			names.append("i/"+ingredient.name)

		return JsonResponse(names, safe=False)
	return render(request, 'lookup.html')

def ingredient(request, ingr_name):
	ingredient = get_object_or_404(Ingredient, name=ingr_name)

	context = {
		'name': ingr_name,
		'sources': ingredient.sources,
		'ox_per_portion': round(ingredient.ox_per_portion),
		'portion_desc': ingredient.portion_desc,
		'portion_grams': ingredient.portion_grams,
		'alternatives': ingredient.alternatives,
		'portion_oz': round(ingredient.portion_grams*.035274,2),
	}
	return render(request, 'ingredient.html', context)

def meal(request, meal_name):
	grams = 0
	oxalates = 0
	ing_ox = 0
	# Loading recipe
	meal = get_object_or_404(Meal, name=meal_name)
	# Finding every connection between meal and ingredients
	connections = get_list_or_404(MealIngredient, meal=meal)

	rows = []

	for meal_ing in connections:
		# Sum up individual oxalate amounts
		ing_ox = meal_ing.ingredient.ox_per_100g * meal_ing.ing_qty_in_g / 100
		oxalates += ing_ox
		# Get grams per meal serving size
		grams += meal_ing.ing_qty_in_g

		ing_name = meal_ing.ingredient.name

		mass_g = float(meal_ing.ing_qty_in_g)
		mass_oz = mass_g * .035274
		mass_value = str(round(mass_g,1)) + " / " + str(round(mass_oz,1))


		rows.append((ing_name, round(ing_ox,1), mass_value))

	# TODO: Get left, right to iterate over ingridient name, oxalate amount and sort in descending order
	rowsorted = sorted(rows, key=lambda tup: tup[1], reverse=True)

	context = {
		'name': meal_name,
		'rows': rowsorted,
		'ox_per_portion': round(oxalates),
		'portion_grams': grams,
		'portion_desc': meal.portion_desc,
		'alternatives': meal.alternatives,
		'source_notes': meal.source_notes,
		'portion_oz': round(float(grams)*.035274,2),
	}

	return render(request, 'meal.html', context)
