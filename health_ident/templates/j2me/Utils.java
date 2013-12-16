package snisi.entities;

import java.util.Vector;
import java.util.Enumeration;
import java.util.Hashtable;
import snisi.entities.StaticCodes;

/**
 * StaticCodes Management
 */

public class Utils {

    public Utils() {

    }

    public static EntityHashTable getTableFromVector(String code, Vector vector) {
        System.out.println("getTableFromVector");

        for(Enumeration elem = vector.elements(); elem.hasMoreElements();) {
            EntityHashTable elem_ht = (EntityHashTable)elem.nextElement();
            if (elem_ht.code.equals(code)) {
                return elem_ht;
            }
        }

        EntityHashTable dummy = new EntityHashTable("dummy", "Dummy");
        return dummy;
    }

    public static String[] getListOfValuesFromVector(Vector vector, boolean return_name) {
        System.out.println("getListOfValuesFromVector");
        int num = vector.size();
        String[] values = new String[num];
        int i = 0;

        for(Enumeration elem = vector.elements(); elem.hasMoreElements();) {
            EntityHashTable elem_ht = (EntityHashTable)elem.nextElement();
            if (return_name) {
                values[i] = elem_ht.name;
            } else {
                values[i] = elem_ht.code;
            }
            i++;
        }
        return values;
    }

    public static String[] regions_codes() {
        System.out.println("regions_codes");
        StaticCodes static_codes = new StaticCodes();
        return getListOfValuesFromVector(static_codes.getRegions(), false);
    }

    public static String[] regions_names() {
        System.out.println("regions_names");
        StaticCodes static_codes = new StaticCodes();
        return getListOfValuesFromVector(static_codes.getRegions(), true);
    }

    public static String[] list_from_enum(Hashtable anHashTable, boolean as_name) {
        int num = anHashTable.size();
        String[] results = new String[num];
        int i = 0;
        Enumeration target;
        if (as_name)
            target = anHashTable.elements();
        else
            target = anHashTable.keys();

        for(Enumeration anEnum = target; anEnum.hasMoreElements();) {
            String result_str = (String)anEnum.nextElement();
            results[i] = result_str;
            i++;
        }
        return results;
    }

    public static String[] districts_codes(String region_code) {
        System.out.println("districts_codes");
        StaticCodes static_codes = new StaticCodes();
        EntityHashTable myregion = getTableFromVector(region_code,
                                                      static_codes.getRegions());
        return list_from_enum(myregion.children_names, false);
    }

    public static String[] districts_names(String region_code) {
        System.out.println("districts_names");
        StaticCodes static_codes = new StaticCodes();
        EntityHashTable myregion = getTableFromVector(region_code,
                                                      static_codes.getRegions());
        return list_from_enum(myregion.children_names, true);
    }

    public static String[] hcenters_codes(String district_code) {

        EntityHashTable mydistrict = districtHashTable(district_code);
        return getListOfValuesFromVector(mydistrict.children, false);
    }

    public static String[] hcenters_names(String district_code) {
        EntityHashTable mydistrict = districtHashTable(district_code);
        return getListOfValuesFromVector(mydistrict.children, true);
    }

    public static String[] villages_codes(String district_code,
                                          String hcenter_code) {
        EntityHashTable mydistrict = districtHashTable(district_code);
        EntityHashTable myhcenter = getTableFromVector(hcenter_code,
                                                       mydistrict.children);

        return getListOfValuesFromVector(myhcenter.children, false);
    }

    public static String[] villages_names(String district_code,
                                          String hcenter_code) {
        EntityHashTable mydistrict = districtHashTable(district_code);
        EntityHashTable myhcenter = getTableFromVector(hcenter_code,
                                                       mydistrict.children);

        return getListOfValuesFromVector(myhcenter.children, true);
    }

    public static EntityHashTable districtHashTable(String district_code) {
        try {
            Class district_cls = Class.forName("snisi.entities.EntityHashTable" + district_code);
            return (EntityHashTable)district_cls.newInstance();
        } catch (Exception e) {
            return new EntityHashTable("dummy", "Dummy");
        }
    }

}
