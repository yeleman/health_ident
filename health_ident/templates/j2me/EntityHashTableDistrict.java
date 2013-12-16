{% load ident %}
package snisi.entities;

import java.util.Vector;

import snisi.entities.EntityHashTable;

/**
 * List of static codes and names for Entities/Locations
 * Automatically generated.
 */


public class EntityHashTable{{ district.slug}} extends EntityHashTable {

    public EntityHashTable{{ district.slug}}() {
        this.code = "{{ district.slug }}";
        this.name = "{{ district.name|safe }}";
        this.children = new Vector();

        {% for cscom in district.get_children %}
        EntityHashTable h{{ cscom.slug }} = new EntityHashTable("{{ cscom.slug }}", "{{ cscom.name|safe }}");

        {% for village in cscom|villages %}
        EntityHashTable v{{ village.slug }} = new EntityHashTable("{{ village.slug }}", "{{ village.name|safe }}");
		h{{ cscom.slug }}.children.addElement(v{{ village.slug }});
       	{% endfor %}

        this.children.addElement(h{{ cscom.slug }});
        {% endfor %}
    }

}