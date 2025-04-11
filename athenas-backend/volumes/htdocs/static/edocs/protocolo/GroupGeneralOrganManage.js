/**
 *
 **/

Ext._define('edocs.protocolo.GroupGeneralOrganManage', {
    extend: 'toolkit.widget.TabPanel',

    getGroupGeneralOrgan: function() {
        if(!this._groupGeneralOrganGrid) {
            this._groupGeneralOrganGrid = Ext._create('edocs.protocolo.GroupGeneralOrganGrid', {
                region: 'north',
                split: true,
                minHeight: 180,
                height: 180,
                hideActions: ['remove']
            });

            this._groupGeneralOrganGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    if(selm.getSelections().length > 0)
                        this.groupGeneralOrgan(selm.getSelections()[0].get('pk'));
                    else
                        this.groupGeneralOrgan(null);
                }
            });
        }

        return this._groupGeneralOrganGrid;
    },

    groupGeneralOrgan: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._groupGeneralOrgan = value;

            if(dispatch)
                this.observerGroupGeneralOrgan();
        }

        return this._groupGeneralOrgan;
    },

    observerGroupGeneralOrgan: function() {
        var value = this.groupGeneralOrgan();

        if(value) {
            this.getControlPanel().enable();

            this.getGeneralOrganGrid().enable();
            this.getGeneralOrganGrid().setParam('in_group_general_organ', value);
            this.getGeneralOrganGrid().setFilterProperty('in_group_general_organ', value, -100);

            this.getGeneralOrganSelectedGrid().enable();
            this.getGeneralOrganSelectedGrid().setParam('in_group_general_organ', value);
            this.getGeneralOrganSelectedGrid().setFilterProperty('in_group_general_organ', value, 100);
        }
        else {
            this.getControlPanel().disable();

            this.getGeneralOrganGrid().disable();
            this.getGeneralOrganGrid().setParam('in_group_general_organ', 0);
            this.getGeneralOrganGrid().setFilterProperty('in_group_general_organ', 0, -100, false);
            this.getGeneralOrganGrid().getStore().removeAll();

            this.getGeneralOrganSelectedGrid().disable();
            this.getGeneralOrganSelectedGrid().setParam('in_group_general_organ', 0);
            this.getGeneralOrganSelectedGrid().setFilterProperty('in_group_general_organ', 0, 100, false);
            this.getGeneralOrganSelectedGrid().getStore().removeAll();
        }
    },

    _addGeneralOrgan: function(pkset) {
        var rest = this.getGroupGeneralOrgan().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'adicionando itens...'});

        mask.show();
        rest.addGeneralOrgan(
            this.groupGeneralOrgan(),
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getGeneralOrganGrid().getStore().reload();
                    this.getGeneralOrganSelectedGrid().getStore().reload();
                    this.getGroupGeneralOrgan().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Adicionando',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    addGeneralOrgan: function(selected) {
        selected = (selected || this.getGeneralOrganGrid().getSelectionModel().getSelections());

        if(selected.length > 0)
            this._addGeneralOrgan(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Adicionando itens',
                msg: 'Primeiro selecione os itens que deseja adicionar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    _removeGeneralOrgan: function(pkset) {
        var rest = this.getGroupGeneralOrgan().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'removendo itens...'});

        mask.show();
        rest.removeGeneralOrgan(
            this.groupGeneralOrgan(),
            pkset,
            {
                scope: this,
                fn: function() {
                    this.getGeneralOrganGrid().getStore().reload();
                    this.getGeneralOrganSelectedGrid().getStore().reload();
                    this.getGroupGeneralOrgan().getStore().reload();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Removendo',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    removeGeneralOrgan: function(selected) {
        selected = (selected || this.getGeneralOrganSelectedGrid().getSelectionModel().getSelections());

        if(selected.length > 0)
            this._removeGeneralOrgan(selected.map(function(data) { return data.get('pk'); }));
        else
            Ext.Msg.show({
                title: 'Adicionando itens',
                msg: 'Primeiro selecione os itens que deseja remover.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getControlPanel: function() {
        if(!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 40,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-add-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.addGeneralOrgan(); }
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-remove-selected',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.removeGeneralOrgan(); }
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-add-all',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {
                            var collection = [];

                            this.getGeneralOrganGrid().getStore().each(
                                function(data) {
                                    collection.push(data);
                                }
                            );

                            this.addGeneralOrgan(collection);
                        }
                    },

                    {
                        xtype: 'button',
                        iconCls: 'icon-core icon-core-remove-all',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {
                            var collection = [];

                            this.getGeneralOrganSelectedGrid().getStore().each(
                                function(data) {
                                    collection.push(data);
                                }
                            );

                            this.removeGeneralOrgan(collection);
                        }
                    },

                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanel;
    },

    getGeneralOrganSelectedGrid: function() {
        if(!this._generalOrganSelectedGrid) {
            var self = this;

            this._generalOrganSelectedGrid = Ext._create('rh.generalorgan.Grid', {
                title: 'Orgãos Selecionados',
                flex: 1.0,
                doubleClickHandler: function() {
                    self.removeGeneralOrgan();
                },
                border: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search',],
                columnAction: false,
            });

        }
        return this._generalOrganSelectedGrid;
    },

    getGeneralOrganGrid: function() {
        if(!this._generalOrganGrid) {
            var self = this;

            this._generalOrganGrid = Ext._create('rh.generalorgan.Grid', {
                title: 'Orgãos Disponíveis',
                flex: 1.0,
                doubleClickHandler: function() {
                    self.addGeneralOrgan();
                },
                border: false,
                gridAutoLoad: false,
                configOrderToolBar: ['search',],
                columnAction: false
            });


            this._generalOrganGrid.setFilterProperty('habilita_protocolo', 'true', 1, false);

        }

        return this._generalOrganGrid;
    },



    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Listas de Distribuição'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getGroupGeneralOrgan(),
                    {
                        region: 'center',
                        layout: 'hbox',
                        minHeight: 150,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getGeneralOrganGrid(),
                            this.getControlPanel(),
                            this.getGeneralOrganSelectedGrid()
                        ]
                    }
                ]
            }
        );

        edocs.protocolo.GroupGeneralOrganManage.superclass.constructor.call(this, cfg);
        this.observerGroupGeneralOrgan();
    }
});
