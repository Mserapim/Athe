Ext._define('rh.raw.Grid', {
    extend: 'core.RestfulGrid',

    constructor: function(cfg) {
        rh.raw.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                this.getColumnModelItems()
            );
        return this._columnModel;
    },

    getColumnModelItems: function(){
        if(!this._columnModelItems){
            this._columnModelItems = [
                Ext._create('Ext.grid.RowNumberer'),
            ];
        }
        // this.setItemsConfig(items, []);
        return this._columnModelItems;
    },

    setItemsConfig: function(items, items_cfg){
        for (key_cfg in items_cfg){
            item_cfg = items_cfg[key_cfg];
            for (key_item in items){
                item = items[key_item];
                if(item.dataIndex == item_cfg.dataIndex && item.dataIndex != undefined){
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
            if(items[key_item].dataIndex == dataIndex){
                items.remove(items[key_item]);
                break;
            }
        }
        return items;
    },
});
