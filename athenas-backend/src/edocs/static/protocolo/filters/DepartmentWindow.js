
Ext._define('edocs.protocolo.filters.DepartmentWindow', {
    extend: 'edocs.protocolo.filters.FilterWindow',

    width: 550,


    getDepartmentField: function(cfg) {
        if(!this._departmentField){
            this._departmentField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Departamento',
                hiddenName: this.nameField,
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('EDOCManage', 'work_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'},
                        ]
                    })
                }),
                width: 395,
                allowBlank: false
            });
        }

        return this._departmentField;
    },

    clearFilter: function() {
        edocs.protocolo.filters.DepartmentWindow.superclass.clearFilter.call(this, {});
        this.fatherGrid.updateTextDepartmentItem();
    },


    applyFilter: function() {
        var display = this.getDepartmentField().getRawValue();

        if(display) {
            this.fatherGrid.updateTextDepartmentItem(display);
        } else {
            this.fatherGrid.updateTextDepartmentItem();
        }

        edocs.protocolo.filters.DepartmentWindow.superclass.applyFilter.call(this, {});
    },


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 120,
                items: [
                    this.getDepartmentField(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Exibir documentos por local de lotação'
            }
        );

        this.nameField = (cfg.nameField !== undefined ? cfg.nameField : "lotacao_destino");

        edocs.protocolo.filters.DepartmentWindow.superclass.constructor.call(this, cfg);

        this.fatherGrid = cfg.grid;
    }
});
