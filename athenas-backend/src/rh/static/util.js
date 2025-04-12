rh.util = {
    setItemsConfig: function(items, items_cfg){
        for (key_cfg in items_cfg){
            item_cfg = items_cfg[key_cfg];
            for (key_item in items){
                item = items[key_item];
                if((item.dataIndex == item_cfg.dataIndex && item.dataIndex != undefined) ||
                        (item.name == item_cfg.name && item.name != undefined)){
                    this.setItemConfig(item, item_cfg);
                }
            }
        }
    },

    setItemConfig: function(item, item_cfg){
        for (cfg in item_cfg){
            value = item_cfg[cfg];
            item[cfg] = value;
        }
    },

    itemRemove: function(items, dataIndex){
        for (key_item in items){
            if((items[key_item].dataIndex == dataIndex) || (items[key_item].name == dataIndex)){
                items.remove(items[key_item]);
            }
        }
        return items;
    },

    getItemFrom: function(items, dataIndex){
        for (key_item in items){
            if((items[key_item].dataIndex == dataIndex) || (items[key_item].name == dataIndex)){
                return items[key_item];
            }
        }
        return undefined;
    }
};