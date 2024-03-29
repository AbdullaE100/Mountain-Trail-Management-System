from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """
    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]
    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        """
        Initializes the DoubleKeyTable instance.

        Parameters:
        ----------
        sizes : list or None
            If provided, the top-level table sizes are set to this value.
            If None, default values from self.TABLE_SIZES are used.

        internal_sizes : list or None
            If provided, the internal table sizes are set to this value.
            If None, default values from self.INTERNAL_TABLE_SIZES are used.

        Attributes:
        ----------
        count : int
            Number of elements in the DoubleKeyTable.

        size_index : int
            Index to track the size of the top-level table for resizing purposes.

        array : ArrayR
            The top-level array that stores internal hash tables.

        Complexity:
        ----------
        Time: O(1)
            Initialization of the instance takes constant time.
        Space: O(n)
            Space complexity is determined by the size of the top-level hash table and internal hash tables.
        """
        if sizes is not None:
            self.TABLE_SIZES = sizes
        else:
            self.TABLE_SIZES = self.TABLE_SIZES
        if internal_sizes is not None:
            self.INTERNAL_TABLE_SIZES = internal_sizes
        else:
            self.INTERNAL_TABLE_SIZES = self.TABLE_SIZES
        self.count = 0
        self.size_index = 0
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        Find the correct position for this key in the hash table using linear probing.

        Parameters:
        ----------
        key1 : K1
            The first key of the key pair.

        key2 : K2
            The second key of the key pair.

        is_insert : bool
            If True, indicates that the method is being called for an insertion operation.
            If False, indicates that the method is being called for a retrieval or deletion operation.

        Returns:
        ----------
        position1 : int
            The position of the first key in the top-level hash table.

        position2 : int
            The position of the second key in the internal hash table.

        Raises:
        ----------
        KeyError:
            When the key pair is not in the table, and is_insert is False.

        FullError:
            When a table is full and cannot be inserted.

        Complexity:
        ----------
        Time: O(1) - Average case
            In most cases, the time complexity of linear probing is constant time.
        Time: O(n) - Worst case
            In the worst case, the time complexity is linear if the table is almost full.
        Space: O(1)
            The space complexity is constant as no additional data structures are used.
        
        """
        position1 = self.hash1(key1)
        probe_count = 0

        while probe_count < self.TABLE_SIZES[self.size_index]:
            if self.array[position1] is None:
                if is_insert:
                    low_level_table = LinearProbeTable(self.INTERNAL_TABLE_SIZES)
                    low_level_table.hash = lambda k: self.hash2(k, low_level_table)
                    self.array[position1] = (key1, low_level_table)  # outer array
                    self.count += 1
                    position2 = self.hash2(key2, low_level_table)
                    return (position1, position2)
                else:
                    raise KeyError(key1)
            elif self.array[position1][0] == key1:
                position2 = self.array[position1][1]._linear_probe(key2, is_insert)
                return (position1, position2)
            else:
                position1 = (position1 + 1) % self.table_size
                probe_count += 1

        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError(key1)

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
            Args:
         key (Optional[K1], optional): If provided, returns an iterator of all keys in the bottom-hash-table for the given key. 
                                  If not provided, returns an iterator of all top-level keys in the hash table.

        Complexity:
            O(n) where n is the number of elements in the hash table.
        """
        if key is None:
            for x in range(self.table_size):
                if self.array[x] is not None:
                    yield self.array[x][0]
        else:
            for x in range(self.table_size):
                if self.array[x] is not None:
                    if self.array[x][0] == key:
                        for y in range(self.array[x][1].table_size):
                            if self.array[x][1].array[y] is not None:
                                yield self.array[x][1].array[y][0]

    def keys(self, key:K1|None=None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        Args:
    key (Optional[K1], optional): If provided, returns all bottom-level keys for the given top-level key. 
                                  If not provided, returns all top-level keys in the table.

        Complexity:
            O(n) where n is the number of elements in the hash table.
        """
        if key is None:
            keys = []
            for x in range (self.table_size):
                if self.array[x] is not None:
                    keys.append(self.array[x][0])
            return keys
        else:
            position = self.hash1(key)
            for _ in range(self.table_size):
                if self.array[position][0] == key:
                    return self.array[position][1].keys()
                else:
                    position = (position + 1) % self.table_size

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        Args:
        key (Optional[K1], optional): If provided, returns an iterator of all values in the bottom-hash-table for the given key. 
                                  If not provided, returns an iterator of all values in the hash table.

        Complexity:
            O(n) where n is the number of elements in the hash table.
        
        """
        if key is None:
            for x in range(self.table_size):
                if self.array[x] is not None:
                    for y in range(self.array[x][1].table_size):
                        if self.array[x][1].array[y] is not None:
                            yield self.array[x][1].array[y][1]
        else:
            for x in range(self.table_size):
                if self.array[x] is not None:
                    if self.array[x][0] == key:
                        for y in range(self.array[x][1].table_size):
                            if self.array[x][1].array[y] is not None:
                                yield self.array[x][1].array[y][1]

    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        Args:
        key (Optional[K1], optional): If provided, returns all values for the given top-level key. 
                                  If not provided, returns all values in the table.

        Complexity:
            O(n) where n is the number of elements in the hash table.
        """
        if key is None:
            keys = []
            for x in range(self.table_size):
                if self.array[x] is not None:
                    keys += self.array[x][1].values()
            return keys
        else:
            position = self.hash1(key)
            for _ in range(self.table_size):
                if self.array[position][0] == key:
                    return self.array[position][1].values()
                else:
                    position = (position + 1) % self.table_size

    def contains(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        Args:
            key (Tuple[K1, K2]): The key to check.

        Returns:
            bool: True if the key is in the hash table, False otherwise.

        Complexity:
            O(1) for the best case, O(n) for the worst case (linear probe).
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: tuple[K1, K2]) -> V:

        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        Args:
            key (Tuple[K1, K2]): The key to get the value for.

        Returns:
            V: The value at the given key.

        Raises:
            KeyError: When the key doesn't exist.

        Complexity:
    O(1) for the best case, O(n) for the worst case (linear probe).
        """
        position1, position2 = self._linear_probe(key[0], key[1], True)
        if self.array[position1] is not None:
            return self.array[position1][1][key[1]]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        Args:
            key (Tuple[K1, K2]): The key to set the value for.
            data (V): The value to set for the given key.

        Complexity:
            O(1) for the best case, O(n) for the worst case (linear probe).
            Additionally, O(n) for rehashing if the table is more than half full.
        """
        position1, position2 = self._linear_probe(key[0], key[1], True)
        self.array[position1][1][key[1]] = data

        if self.count > self.table_size/2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        Copy code
        Args:
            key (Tuple[K1, K2]): The key to delete.

        Raises:
            KeyError: When the key doesn't exist.

        Complexity:
            O(1) for the best case, O(n) for the worst case (linear probe).
        """
        k1, k2 = key
        try:
            position1, position2 = self._linear_probe(k1, k2, False)
            del self.array[position1][1][k2]
            if len(self.array[position1][1]) == 0:
                self.array[position1] = None
                self.count -= 1
        except KeyError:
            raise KeyError(key)

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
            Complexity:
        Best case: O(N * hash(K)) where no probing is required.
        Worst case: O(N * hash(K) + N^2 * comp(K)) where lots of probing is required.
        N is the number of elements in the hash table.
        """
        old_array = self.array
        self.size_index += 1
        if self.size_index == len(self.TABLE_SIZES):
            # Cannot be resized further.
            return
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0
        for item in old_array:
            if item is not None:
                key, value = item
                pos = self.hash1(key)
                self.array[pos] = (key,value)

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        Returns:
            int: The size of the table.

        Complexity:
            O(1)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        Returns:
        int: The number of elements in the hash table.

        Complexity:
            O(n) where n is the number of elements in the hash table.
        """
        return len(self.values())

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()