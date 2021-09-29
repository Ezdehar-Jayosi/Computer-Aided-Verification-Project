

//returns n!
int factorial_v1 (int n){
	int i;
	int n_factorial = 1;
	for (i = 1; i <= n; i++){
		n_factorial = n_factorial*i;
	}
	return n_factorial;
}

//same, but using a while loop
int factorial_v2 (int n){
	int n_factorial = 1;
	int i = 1;
	while (i <= n){
		i++;
		n_factorial = n_factorial*i;
	}
	return n_factorial;
}

//same, but using a do while loop
int factorial_v3 (int n){
	int n_factorial = 1;
	int i = 0;
	do {
		i++;
		n_factorial = n_factorial*i;
	}
	while (i < n);
	return n_factorial;
}

//returns 1+2+...+n
int sum (int n){
	int n_factorial, i, j;
	int n_sum = 0;
	for (i = 1; i <= n; i++){
		for (j = 0; j < i; j++) {
			n_sum++;
		}
	}
	return n_sum;
}

