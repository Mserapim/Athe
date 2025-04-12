/**
 *
 **/
Ext._define('core.fields.MultiSelectField', {
    extend: 'Ext.form.CompositeField',

    xtype: 'multiselectfield',

    enable: function() {
        this.getGridPanel().enable();
        this.getAddField().enable();
    },

    disable: function() {
        this.getGridPanel().disable();
        this.getAddField().disable();
    },

    getValues: function() {
        return this.getGridPanel().getStore().data.keys.toString();
    },

    getColumModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                {
                    header: 'Descrição',
                    dataIndex: cfg.gridField,
                    id: 'autoExpandId',
                    sortable: false
                }
            ]);

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar)
            this._toolbar = Ext._create('Ext.Toolbar', {
                items: [
                    'Buscar ',
                    ' : ',
                    ' ',
                    this.getAddField(cfg)
                ]
            });

        return this._toolbar;
    },

    getFooterBar: function(cfg) {
        if(!this._footerBar)
            this._footerBar = Ext._create('Ext.Toolbar', {
                items: [
                    '->',
                    '-',
                    {
                        text: 'Limpar',
                        iconCls: 'icon-core icon-core-clear',
                        scope: this,
                        handler: this.deleteItems
                    }
                ]
            });

        return this._footerBar;
    },

    factoryRestful: function(cfg) {
        if(cfg)
            return Ext._create(cfg.rest);
        else
            return Ext._create(this.rest);
    },

    setSize: function(w, h) {
        this.getAddField().setWidth(w - 60);
        this.getGridPanel().setSize(w - 2, h - 20);
        core.fields.MultiSelectField.superclass.setSize.call(this, w, h);
    },

    getGridPanel: function(cfg) {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('Ext.grid.GridPanel', {
                border: true,
                title: cfg.title,
                height: (cfg.height ? cfg.height - 30: 300),
                bodyStyle: {border: '1px solid #99bbe8'},
                autoExpandColumn: 'autoExpandId',
                bbar: this.getFooterBar(cfg),
                tbar: this.getToolbar(cfg),
                cm: this.getColumModel(cfg),
                store: [],
            });
        return this._gridPanel;
    },

    deleteItems: function() {
        var selected = this.getGridPanel().getSelectionModel().getSelected();
        if (selected) {
            this.getGridPanel().getStore().remove(selected);
        } else {
            Ext.Msg.show({
                title: 'Exclusão de Item',
                msg: 'Selecione um item para removê-lo.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    addItem: function(record) {
        var found = this.getGridPanel().getStore().find('pk', record.data.pk);
        if(found < 0){
            this.getGridPanel().getStore().addSorted(record);
        }
        this.getAddField().getComboField().setValue('');
    },

    getAddField: function(cfg) {
        if(!this._addField) {
            this._addField = Ext._create('core.fields.AutocompleteField',  {
                rest: cfg.rest,
                fieldLabel: 'Test',
                submitValue: false,
                width: 100,
                displayField: cfg.findField,
                valueField: cfg.valueField,
                emptyText: cfg.emptyText,
                preFilter: cfg.preFilter,
                gridConfig: cfg.gridConfig,
                comboListeners: {
                    scope: this,
                    select: function(combo, record, index) {
                        this.addItem(record);
                    },
                }
            });

            if((cfg || this).preFilter)
                this._addField.setPreFilter((cfg || this).preFilter);
        }

        return this._addField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                style: {
                    borderWidth: 1
                },
                height: 300,
                gridField: cfg.gridField ? cfg.gridField : cfg.displayField,
                findField: cfg.findField ? cfg.findField : cfg.displayField,
                valueField: 'pk',
                emptyText: 'Escreva para localizar item',
            }
        );
        if(!cfg.rest)
            throw 'Você precisa definir o objeto Restful do relacionamento.';
        Ext.apply(
            cfg,
            {
                items: [
                    {
                        xtype: 'panel',
                        width: cfg.width,
                        border: core.nullValue(cfg.border, false),
                        items: [
                            {
                                xtype: 'textfield',
                                submitValue: false,
                                inputType: 'hidden'
                            },
                            this.getGridPanel(cfg)
                        ]
                    }
                ]
            }
        );
        core.fields.MultiSelectField.superclass.constructor.call(this, cfg);
    }
});
