Ext._define('rh.person.merge.GenericGrid', {
    extend: 'Ext.grid.GridPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        var data = [];
        cfg.data.forEach(function(item){
            data.push([item.pk, item.unicode, item.person_unicode])
        });

        var sm = this.getSm({});
        var columns = cfg.columns || this.getColumns({});

        var includes = false;
        columns.forEach(function(item){
            if(item._name == 'checkSm')
                includes = true;
        });

        if(cfg.sm == undefined && includes == false){
            columns.push(sm);
            Ext.apply(cfg, {sm: sm});
        }

        Ext.applyIf(
            cfg,
            {
                region: 'center',
                title: '',
                store: this.getStore({data: data, fields: cfg.fieldsStore}),
                columns: columns,
                height: 480,
                frame: true,
            }
        );
        rh.person.merge.GenericGrid.superclass.constructor.call(this, cfg);
    },

    getStore: function(cfg){
        if(!this._store){
            Ext.applyIf(
                cfg,
                {
                    fields: ['pk', 'unicode'],
                }
            );
            this._store = Ext._create('Ext.data.ArrayStore', cfg);
        }
        return this._store;
    },

    getSm: function(cfg){
        if(!this._sm){
            this._sm = Ext._create('Ext.grid.CheckboxSelectionModel', cfg);
        }
        return this._sm;
    },

    getColumns: function(cfg){
        return [
            {header: 'Chave', dataIndex:'pk'},
            {header: 'Servidor', dataIndex: 'unicode',id: 'autoExpandColumn', width: 460},
        ];
    }
});
