
package snisi.entities;

import java.util.Vector;

import snisi.entities.EntityHashTable;
{% for region in regions %}{% for district in region.get_children %}
import snisi.entities.EntityHashTable{{ district.code }};
{% endfor %}{% endfor %}

/**
 * List of static codes and names for Entities/Locations
 * Automatically generated.
 */


public class StaticCodes {

    public EntityHashTable root;

    public Vector getRegions() {
        return root.children;
    }

    public StaticCodes() {

        root = new EntityHashTable("mali", "Mali");

        {% for region in regions %}
        EntityHashTable r{{ region.code }} = new EntityHashTable("{{ region.code }}", "{{ region.name|safe }}");
        root.children.addElement(r{{ region.code }});

        {% for district in region.get_children %}
        r{{ region.code }}.children_names.put("{{ district.code }}", "{{ district.name|safe }}");
        {% endfor %}
        {% endfor %}
    }

}
