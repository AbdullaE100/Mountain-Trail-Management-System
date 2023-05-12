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
        """
        position1 = self.hash1(key1)
        for _ in range(self.TABLE_SIZES[self.size_index]):
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
        # if key is None:
        #     for x in range(self.table_size):
        #         if self.array[x] is not None:
        #             yield self.array[x][0]
        # else:
        #     position = self.hash1(key)
        #     for _ in range(self.table_size):
        #         if self.array[position][0] == key:
        #             for k in self.array[position][1].keys():
        #                 yield k
        #             return
        #         else:
        #             position = (position + 1) % self.table_size
        # return

    def keys(self, key:K1|None=None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
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
        # if key is None:
        #     keys = []
        #     for i in range(self.table_size):
        #         if self.array[i] is not None:
        #             keys.append(self.array[i][0])
        #     return keys
        # else:
        #     position = self.hash_func(key)
        #     for i in range(self.table_size):
        #         if self.array[position] is None:
        #             raise KeyError(f"Key {key} not found in hash table.")
        #         elif self.array[position][0] == key:
        #             if isinstance(self.array[position][1], dict):
        #                 return list(self.array[position][1].keys())
        #             else:
        #                 raise ValueError(f"Sub-table for key {key} is not a dictionary.")
        #         else:
        #             position = (position + 1) % self.table_size
        #     raise KeyError(f"Key {key} not found in hash table.")

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
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
        """
        position1, position2 = self._linear_probe(key[0], key[1], True)
        if self.array[position1] is not None:
            return self.array[position1][1][key[1]]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        position1, position2 = self._linear_probe(key[0], key[1], True)
        self.array[position1][1][key[1]] = data

        if self.count > self.table_size/2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
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
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return len(self.values())

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()