int BinarySearch (int a[], int len, int key) {
    int low = 0;
    int high = len;
    while (low < high) {
        int half_1 = high/2;
        int half_2 = low/2;
        int mid = low + half_1 - half_2;
        int val = a[mid];
        if (key < val) {
            low = mid + 1;
        } 
        else if (val < key) {
            high = mid;
        } 
        else {
            return mid;
        }
    }
    return len + 1;
}