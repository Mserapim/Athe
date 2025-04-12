/**
 *
 **/
Ext._define('core.fields.AutocompleteField', {
    extend: 'Ext.form.CompositeField',

    xtype: 'rest-autocompletefield',

    factoryRestful: function(classname) {
        var cname = core.nullValue(this.rest, classname);

        return Ext._create(cname);
    },

    setValue: function(value) {
        this.getComboField().setValue(value);
        // console.debug('SET VALUE: '+value);
    },

    getValue: function() {
        return this.getComboField().getValue();
    },

    getRawValue: function() {
        return this.getComboField().getRawValue();
    },

    setStore: function(store) {
        this.store = store;
        this.getComboField().setStore(store);
    },

    getComboField: function(cfg) {
        if(!this._comboField) {
            this._comboField = Ext._create(
                'core.fields.ComboField',
                this.configureCombo(cfg)
            );

            this.setPreFilter(cfg.preFilter);

            if(cfg.baseParams){
                for(var x in cfg.baseParams) {
                    this._comboField.getStore().setBaseParam(x, cfg.baseParams[x]);
                }
            }

            if(cfg.safeMode) {
                this._comboField.on({
                    scope: this,
                    render: function(c) {
                        c.getEl().on({
                            scope: this,
                            click: function() {
                                this.selectionWindow();
                            }
                        });
                    }
                });
            }
        }


        return this._comboField;
    },

    configureCombo: function(cfg) {
        var config = {};
        cfg = core.nullValue(cfg, this);

        config = {
            readOnly: core.nullValue(cfg.safeMode, false),
            minChars: core.nullValue(cfg.minChars, 3),
            hiddenName: cfg.name,
            name: cfg.name,
            rest: cfg.rest,
            displayField: cfg.displayField,
            valueField: cfg.valueField,
            value: cfg.value,
            tpl: cfg.tpl,
            triggerAction: 'all',
            hideTrigger: true,
            resizable: true,
            emptyText: cfg.emptyText,
            listeners: cfg.comboListeners,
            flex: 1.0,
            queryParam: 'keyword',
            autoLoad: false,
            mode: 'remote',
            submitValue: cfg.submitValue,
            store: cfg.store,
            tabIndex: cfg.tabIndex,
            enableKeyEvents: cfg.enableKeyEvents || false,
            allowBlank: core.nullValue(cfg.allowBlank, true)
        };

        if(cfg.safeMode) {
            config.style = {
                paddingLeft: '5px',
                background: '#f5fff5',
                border: '1px solid #7a7',
                borderBottomWidth: '2px',
                color: '#373'
            };
        }

        return config;
    },

    setPreFilter: function(preFilter) {
        this.preFilter = preFilter;

        if(this._comboField) {
            this._comboField.getStore().baseParams.filter = Ext.encode(
                core.nullValue(this.preFilter, [])
            );

            this.setValue(this.getValue());
        }
    },

    selectionWindow: function() {
        var wnd;

        this.gridConfig = core.nullValue(this.gridConfig, {});

        //FIXME: será removido em 10/2013
        if(!this.gridConfig && (this.gridColumnAction !== undefined || this.gridListeners !== undefined || this.gridAutoLoad !== undefined)) {
            console.warn('The gridColumnAction, gridListeners and gridAutoLoad is deprecated use gridConfig');
            Ext.apply(this.gridConfig, {
                columnAction: this.gridColumnAction,
                listeners: this.gridListeners,
                gridAutoLoad: this.gridAutoLoad
            });
        }

        if(this.preFilter) {
            Ext.apply(this.gridConfig, {
                preFilter: this.preFilter
            });
        }

        // this.gridConfig.store = this.getComboField().getStore();
        this.gridConfig.storeCustom = this.getComboField().getStore();

        Ext.apply(this.gridConfig, {baseParams: core.nullValue(this.baseParams, {})});

        this.gridConfig.doubleClickHandler = function(grid) {
            wnd.commitSelection(true);
        };

        wnd = Ext._create('core.fields.AutocompleteSelectionWindow', {
            rest: this.rest,
            values: [this.getValue()],
            field: this,
            safeMode: this.safeMode,
            gridConfig: this.gridConfig,
            valueField: this.valueField
        }).show();
    },

    getButton: function() {
        if(!this._button)
            this._button = Ext._create('Ext.Button',{
                text: '...',
                width: 22,
                scope: this,
                handler: this.selectionWindow
            });

        return this._button;

    },

    enable: function() {
        this.getComboField().enable();
        this.getButton().enable();
    },

    disable: function() {
        this.getComboField().disable();
        this.getButton().disable();
    },

    setReadOnly: function(enable) {
        this.getComboField().setReadOnly(enable);

        if(!enable)
            this.getButton().enable();
        else
            this.getButton().disable();
    },

    setBaseParam: function(name, value) {
        if(this.store){
            this.store.setBaseParam(name, value);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(!cfg.rest) throw 'Nenhum objeto Restful foi informado e este é obrigatório.';

        Ext.applyIf(
            cfg,
            {
                displayField: 'unicode',
                valueField: 'pk',
                emptyText: 'Escreva para localizar item',
                gridColumnAction: true
            }
        );

        cfg.tpl = '<tpl for="."><div class="x-combo-list-item">{' + cfg.displayField + '}</div></tpl>';

        Ext.apply(
            cfg,
            {
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getComboField(cfg),
                    this.getButton()
                ]
            }
        );

        // this.callParent([cfg]);
        core.fields.AutocompleteField.superclass.constructor.call(this, cfg);

    }
});
