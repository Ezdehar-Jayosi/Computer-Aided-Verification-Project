int BinarySearch (int a[], int len, int key){
    int low = 0;
    int high = len;
    while (low < high){
        int mid = low + (high − low) / 2;
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
    return −1;
}