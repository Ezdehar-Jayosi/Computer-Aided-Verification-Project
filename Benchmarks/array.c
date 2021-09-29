void assert(int cond);

#define N 100
#define SWAP(X,Y) { tmp = (X); (X) = (Y); (Y) = tmp; }
#define ENSURES(function, condition)  inline void ensures_##function() {ensures_##function(condition);}

/**
 * Computes the maximal of three array elements.
 *
 * @ensures ((ret == arr[i]) || (ret == arr[j]) || (ret == arr[k]))
 *            && (ret <= arr[i]) && (ret <= arr[j]) && (ret <= arr[k])
 *
 *
 */

ENSURES(max3_array, ((ret == arr[i]) || (ret == arr[j]) || (ret == arr[k]))
            	&& (ret <= arr[i]) && (ret <= arr[j]) && (ret <= arr[k]))
int max3_array(int arr[N], int i, int j, int k) {
    if (arr[i] < arr[j]) {
        if (arr[i] < arr[k]) return arr[i];
    }
    else {
        if (arr[j] < arr[k]) return arr[j];
    }
    return arr[k];
}

/**
 * Same, but indices are also given as an array.
 *
 * @ensures ((ret == arr[is[0]]) || (ret == arr[is[1]]) || (ret == arr[is[2]]))
 *            && (ret <= arr[is[0]]) && (ret <= arr[is[1]]) && (ret <= arr[is[2]])
 */

ENSURES(max3_array_indirect,
		((ret == arr[is_arr[0]]) || (ret == arr[is_arr[1]]) || (ret == arr[is_arr[2]]))
		&& (ret <= arr[is_arr[0]]) && (ret <= arr[is_arr[1]]) && (ret <= arr[is_arr[2]]))
int max3_array_indirect(int arr[N], int is_arr[3]) {
    if (arr[is_arr[0]] < arr[is_arr[1]]) {
        if (arr[is_arr[0]] < arr[is_arr[2]]) return arr[is_arr[0]];
    }
    else {
        if (arr[is_arr[1]] < arr[is_arr[2]]) return arr[is_arr[1]];
    }
    return arr[is_arr[2]];
}


void sort3(int arr[N], int i) {
    int tmp;

    if (arr[i] > arr[i + 1]) SWAP(arr[i], arr[i + 1]);
    if (arr[i + 1] > arr[i + 2]) SWAP(arr[i + 1], arr[i + 2]);
    if (arr[i] > arr[i + 1]) SWAP(arr[i], arr[i + 1]);

    /**/ assert((arr[i] <= arr[i + 1]) && (arr[i + 1] <= arr[i + 2])); /**/
}
