/**
 *
 **/
Ext._define('core.fields.RelatedRestfulField', {
    extend: 'Ext.form.CompositeField',

    xtype: 'rest-relatedfield',

    enable: function() {
        this.getGridPanel().enable();
        this.getAddField().enable();
    },

    disable: function() {
        this.getGridPanel().disable();
        this.getAddField().disable();
    },

    objectId: function(objectId) {
        if(objectId !== undefined) {
            var older = this.oId;
            this.oId = objectId;
            this.fireEvent('objectIdChanged', older, this.oId);
        }
        else
            return this.oId;
    },

    observeObjectId: function() {
        if(this.oId) {
            this.enable();
            this.getGridPanel().reconfigure(
                this.factoryStore(),
                this.getColumModel()
            );
            this.getGridPanel().getStore().load();
        }
        else {
            this.disable();
            // this.getGridPanel().setStore([]);
        }
    },

    getColumModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                {
                    header: 'Descrição',
                    dataIndex: 'unicode',
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

    openSelectWindow: function() {
        var cfg = {
            selected: [],
            field: this
        };

        if(this.preFilter)
            cfg.preFilter = this.preFilter;

        Ext._create('core.fields.RelatedSelectWindow', cfg).show();
    },

    getFooterBar: function(cfg) {
        if(!this._footerBar)
            this._footerBar = Ext._create('Ext.Toolbar', {
                items: [
                    {
                        text: 'Selecionar',
                        iconCls: 'icon-core icon-core-select',
                        scope: this,
                        handler: this.openSelectWindow,
                        disabled: this.hideSelectButton,
                    },
                    '-',
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

    factorySourceRestful: function(cfg) {
        if(cfg)
            return Ext._create(cfg.sourceRest);
        else
            return Ext._create(this.sourceRest);
    },

    factoryStore: function(cfg) {
        var configStore = {
            reader: Ext._create('Ext.data.JsonReader', {
                root: 'collection',
                totalProperty: 'count',
                fields: [
                    {name: 'pk', type: 'int'},
                    {name: 'unicode', type: 'string'}
                ]
            }),
            baseParams: {
                field: (this || cfg).name,
                limit: 9999
            }
        };

        if(this.objectId() || (cfg && cfg.oId)) {
            Ext.apply(configStore, {
                proxy: Ext._create('Ext.data.HttpProxy',
                    this.factoryRestful(cfg || this).getRoute('related', (this.objectId() || cfg.oId))
                )
            });
        }

        return Ext._create('Ext.data.Store', configStore);
    },

    setSize: function(w, h) {
        this.getAddField().setWidth(w - 60);
        this.getGridPanel().setSize(w - 2, h - 20);
        core.fields.RelatedRestfulField.superclass.setSize.call(this, w, h);
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
                store: this.factoryStore(cfg),
                loadMask: true
            });

        return this._gridPanel;
    },

    deleteItems: function() {
        var selection = this.getGridPanel().getSelectionModel().getSelections();
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {
            msg: 'Retirando itens...'
        });
        var xhrConf = rest.getRoute('related', this.objectId());

        Ext.apply(xhrConf, {
            method: 'DELETE',
            params: {
                field: this.name
            },
            scope: this,
            callback: function() {
                mask.hide();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success)
                    this.getGridPanel().getStore().reload();
                else
                    Ext.Msg.show({
                        title: 'Retirando itens',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
            },
            failure: function(request) {
                Ext.Msg.show({
                    title: 'Retirando itens',
                    icon: Ext.Msg.OK,
                    buttons: Ext.Msg.ERROR,
                    msg: 'Ocorreu um erro tentando acessar o recurso, tente novamente mais tarde.'
                });

            }
        });

        if(selection.length > 0) {
            Ext.Msg.show({
                title: 'Retirando dados',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja retirar os itens selecionados?',
                scope: this,
                fn: function(b) {
                    if(b=='no') return;

                    xhrConf.params[this.name] = selection.map(
                        function(data) {
                            return data.get('pk');
                        }
                    );

                    mask.show();
                    rest.doRequest(xhrConf);
                }
            });
        }
        else {
            Ext.Msg.show({
                title: 'Retirando dados',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja retirar todos itens?',
                scope: this,
                fn: function(b) {
                    if(b=='no') return;

                    mask.show();
                    rest.doRequest(xhrConf);
                }
            });
        }
    },

    addItem: function(item) {
        var xhrConf;
        var rest;
        var mask;

        if(item && this.objectId()) {
            rest = this.factoryRestful();
            mask = new Ext.LoadMask(this.getEl(), {
                msg: 'Persistindo dados...'
            });

            xhrConf = rest.getRoute('related', this.objectId());
            Ext.apply(xhrConf, {
                method: 'POST',
                params: {},
                scope: this,
                callback: function() {
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    if(rst.success)
                        this.getGridPanel().getStore().reload();
                    else
                        Ext.Msg.show({
                            title: 'Persistindo dados',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(request) {
                    Ext.Msg.show({
                        title: 'Persistindo dados',
                        icon: Ext.Msg.OK,
                        buttons: Ext.Msg.ERROR,
                        msg: 'Ocorreu um erro tentando acessar o recurso, tente novamente mais tarde.'
                    });

                }
            });

            xhrConf.params[this.name] = item;
            xhrConf.params.field = this.name;
            this.getAddField().setValue('');

            mask.show();
            rest.doRequest(xhrConf);
        }
    },

    getAddField: function(cfg) {
        if(!this._addFeidl) {
            this._addFeidl = Ext._create('core.fields.AutocompleteField',  {
                rest: cfg.sourceRest,
                fieldLabel: 'Test',
                submitValue: false,
                width: 100,
                displayField: cfg.displayField,
                valueField: cfg.valueField,
                emptyText: cfg.emptyText,
                comboListeners: {
                    scope: this,
                    select: function(combo) {
                        this.addItem(combo.getValue());
                    },
                    specialkey: function(combo, event) {
                        if(event.getKey() == event.ENTER)
                            this.addItem(combo.getValue());
                    }
                },
                gridConfig: cfg.gridConfig,
            });

            if((cfg || this).preFilter)
                this._addFeidl.setPreFilter((cfg || this).preFilter);
        }

        return this._addFeidl;
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
                displayField: 'unicode',
                valueField: 'pk',
                emptyText: 'Escreva para localizar item',
            }
        );

        if(!cfg.rest)
            throw 'Você precisa definir o objeto Restful do relacionamento.';

        if(!cfg.sourceRest)
            throw 'Você precisa definir o objeto Source Restful do relacionamento.';


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


        // this.callParent([cfg]);
        core.fields.RelatedRestfulField.superclass.constructor.call(this, cfg);

        this.addEvents('objectIdChanged');
        this.addListener('objectIdChanged', this.observeObjectId, this);
        this.fireEvent('objectIdChanged');
    }
});
