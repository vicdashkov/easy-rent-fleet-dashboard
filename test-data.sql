INSERT INTO public.location(
	name, address)
	VALUES ('test-hotel', '2-22 phuket st');

INSERT INTO public.bike(
	name, mileage, location, plates)
	VALUES ('test-bike', 1, 1, 'v771');

INSERT INTO public.customer(
	l_name, f_name, location, phone, email, notes)
	VALUES ('cus l name', 'cus f name', 1, '+1-878-2222-222', 'cus@email.com', '');

INSERT INTO public."user"(
	type, l_name, f_name)
	VALUES (1, 'test-user l name', 'test user f name');

INSERT INTO public."order"(
	start, "end", cus_id, amount, a_currency,
	mileage_start, mileage_end, bike, notes,
	location_start, location_end, deposit,
	d_currency, assign_p_up, assign_d_off)
	VALUES ('2016-06-22 19:10:25-07', '2016-06-23 19:10:25-07', 1, 100, 'RUB',
			1, 1, 1, '',
			1, 1, 50,
			'RUB', 1, 1);
