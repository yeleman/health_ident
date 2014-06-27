{% load ident %}
package snisi.entities;

import java.util.Vector;

import snisi.entities.EntityHashTable;

/**
 * List of static codes and names for Entities/Locations
 * Automatically generated.
 */


public class EntityHashTable{{ district.code}} extends EntityHashTable {

    public EntityHashTable{{ district.code}}() {
        this.code = "{{ district.code }}";
        this.name = "{{ district.name|safe }}";
        this.children = new Vector();

        {% for harea in district.get_children %}
        EntityHashTable h{{ harea.code }} = new EntityHashTable("{{ harea.code }}", "{{ harea.name|safe }}");

        {% for village in harea|villages %}
        EntityHashTable v{{ village.code }} = new EntityHashTable("{{ village.code }}", "{{ village.name|safe }}");
		h{{ harea.code }}.children.addElement(v{{ village.code }});
       	{% endfor %}

        this.children.addElement(h{{ harea.code }});
        {% endfor %}
    }

}