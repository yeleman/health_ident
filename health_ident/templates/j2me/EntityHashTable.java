package snisi.entities;

import java.util.Vector;
import java.util.Hashtable;

public class EntityHashTable {

    public String code;
    public String name;
    public Vector children = new Vector();
    public Hashtable children_names = new Hashtable();

    public EntityHashTable() {
    }

    public EntityHashTable(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public EntityHashTable(String code, String name, Vector children) {
        this.code = code;
        this.name = name;
        this.children = children;
    }

}