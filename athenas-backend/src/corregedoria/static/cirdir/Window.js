Ext._define('corregedoria.cirdir.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.Restful',
    width: 1100,
    height: 650,

    getAddressGrid: function(item) {
        if(!this._addressGrid) {
            this._addressGrid = Ext._create('corregedoria.cirdir.address.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'person_id': item.values.person_id,
                  'controlinformation': item.values.pk,
                  'closed_address': item.values.closed_address,
                  'mainGrid': item.params.mainGrid,
                }
           });
           this._addressGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selected = sel.getSelected();
                   if(selected){
                       this.observerType(this._addressGrid, {type: 'address', value:selected.get('pk')});
                   } else {
                       this.observerType(null, {type: 'address', value: null});
                   }
               }
           });
       }
       return this._addressGrid;
    },

    getTabAddress: function(cfg) {
        if(!this._tabAddress) {
            this._tabAddress = Ext._create('Ext.Panel', {
                title: 'RESIDÊNCIA',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getAddressGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 510,
                                style: {marginLeft: '10px'},
                                items: [
                                    this.factoryTile('address')
                                ]
                            },
                        ]
                    },
                ],
            });
        }
        return this._tabAddress;
    },

    getTeachingGrid: function(item) {
        if(!this._teachingGrid) {
            this._teachingGrid = Ext._create('corregedoria.cirdir.teaching.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.values.pk,
                  'closed_teaching': (item.values.closed_teaching_1st_semestry && item.values.closed_teaching_2nd_semestry) ? true : false,
                  'mainGrid': item.params.mainGrid,
                },
           });

           this._teachingGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selected = sel.getSelected();
                   if(selected){
                       this.observerType(this._teachingGrid, {type: 'teaching', value:selected.get('pk')});
                   } else {
                        this.observerType(null, {type: 'teaching', value: null});
                   }
               }
           });
       }
       return this._teachingGrid;
    },

    getTabTeaching: function(cfg) {
        if(!this._tabTeaching) {
            this._tabTeaching = Ext._create('Ext.Panel', {
                title: 'DOCÊNCIA',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getTeachingGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 510,
                                style: {marginLeft: '10px'},
                                items: [
                                    this.factoryTile('teaching')
                                ]
                            },
                        ]
                    },
                ],
            });
        }
        return this._tabTeaching;
    },

    getPropertyGrid: function(item) {
        if(!this._propertyGrid) {
            this._propertyGrid = Ext._create('corregedoria.cirdir.property.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.values.pk,
                  'closed_property': item.values.closed_property,
                  'year': item.values.year,
                  'previous_year': item.values.previous_year,
                  'mainGrid': item.params.mainGrid,
                },
           });

           this._propertyGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selected = sel.getSelected();
                   if(selected){
                       this.observerType(this._propertyGrid, {type: 'property', value:selected.get('pk')});
                   } else {
                       this.observerType(null, {type: 'property', value: null});
                   }
               }
           });
       }
       return this._propertyGrid;
    },

    getTabProperty: function(cfg) {
        if(!this._tabProperty) {
            this._tabProperty = Ext._create('Ext.Panel', {
                title: 'BENS E DIREITOS',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getPropertyGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 510,
                                style: {marginLeft: '10px'},
                                items: [
                                    this.factoryTile('property')
                                ]
                            },
                        ]
                    },
                ],
            });
        }
        return this._tabProperty;
    },

    getDebitsGrid: function(item) {
        if(!this._debitsGrid) {
            this._debitsGrid = Ext._create('corregedoria.cirdir.debits.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.values.pk,
                  'closed_debits': item.values.closed_debits,
                  'mainGrid': item.params.mainGrid,
                },
           });

           this._debitsGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selected = sel.getSelected();
                   if(selected){
                       this.observerType(this._debitsGrid, {type: 'debits', value:selected.get('pk')});
                   } else {
                       this.observerType(null, {type: 'debits', value: null});
                   }
               }
           });
       }
       return this._debitsGrid;
    },

    getTabIRPF: function(cfg) {
        if(!this._tab_attach_irpf) {
            this._tab_attach_irpf = Ext._create('Ext.Panel', {
                title: 'DECLARAÇÃO IRPF',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 1,
                        columnWidth: 0.50,
                        items: [
                            this.getAttachIRPFGrid(cfg),
                        ]
                    }
                ],
            });
        }
        return this._tab_attach_irpf;
    },

    getAttachIRPFGrid: function(item) {
        if(!this._attach_irpf) {
            this._attach_irpf = Ext._create('corregedoria.cirdir.irpf.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.values.pk,
                  'closed_irpf': item.values.closed_irpf,
                  'mainGrid': item.params.mainGrid,
                  'employee_type': item.values.employee_type,
                },
           });

           this._attach_irpf.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selected = sel.getSelected();
                   if(selected){
                       this.observerType(this._attach_irpf, {type: 'irpf', value:selected.get('pk')});
                   } else {
                       this.observerType(null, {type: 'irpf', value: null});
                   }
               }
           });
       }
       return this._attach_irpf;
    },

    createDetailPanel: function(type) {
        var TilePanelDetail = Ext._create('core.TilePagePanel', {
            split: true,
            papperModel: 'card',
            id: 'tile_panel_for_'+type
        });
        return TilePanelDetail;
    },

    observerType: function(grid, params) {

        var detail = this.factoryTile(params.type)

        if((params || {}).value) {
            this.readInfo(grid.rest, params, detail);
        } else {
            detail.setPageContent('');
            detail.disable();
        }
    },

    factoryTile: function(typeInfo) {

        if(!this._tileGroup) {
            this._tileGroup = new Map();
        }

        if(this._tileGroup.get(typeInfo) == undefined) {
            this._tileGroup.set(typeInfo, this.createDetailPanel(typeInfo));
        }

        return this._tileGroup.get(typeInfo);
    },

    readInfo: function(rest, params, tilePanel) {
        var mask = new Ext.LoadMask(tilePanel.getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create(rest);
        mask.show();
        tilePanel.enable();
        tilePanel.setPageContent('');

        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: params,
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    tilePanel.setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    getTabDebits: function(cfg) {
        if(!this._tabDebits) {
            this._tabDebits = Ext._create('Ext.Panel', {
                title: 'DÍVIDAS E ÔNUS REAIS',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getDebitsGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 510,
                                style: {marginLeft: '10px'},
                                items: [
                                    this.factoryTile('debits')
                                ]
                            },
                        ]
                    },
                ],
            });
        }
        return this._tabDebits;
    },

    getHealthGrid: function(item) {
        if(!this._healthGrid) {
            this._healthGrid = Ext._create('corregedoria.cirdir.health.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: false,
                height: 510,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                  'controlinformation': item.values.pk,
                  'closed_health': item.values.closed_health,
                  'mainGrid': item.params.mainGrid,
                  'health_area': item.params.health_area,
                },
           });

           this._healthGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelected();
                   this.health(selection !== undefined ? selection.get('pk') : null);
               }
           });
       }
       return this._healthGrid;
    },

    getTilePanelAssessment: function() {
        if(!this._tilePanelAssessment) {
            this._tilePanelAssessment = Ext._create('core.TilePagePanel', {
                title: 'Recomendações',
                split: true,
                papperModel: 'card',
            });
        }
        return this._tilePanelAssessment;
    },

    getTilePanelHealth: function() {
        if(!this._tilePanelHealth) {
            this._tilePanelHealth = Ext._create('core.TilePagePanel', {
                title: 'Questionário',
                split: true,
                papperModel: 'card',
            });
        }
        return this._tilePanelHealth;
    },

    tabHealthActivated: function(tabpanel, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(tabpanel !== undefined) {
            this._healthTabActivated = tabpanel;
            if(dispatch) this.observerHealth();
        }

        return this._healthTabActivated;
    },

    health: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._health = value;
            if(dispatch)
                this.observerHealth();
        }

        return this._health;
    },

    observerHealth: function() {
        var value = this.health();

        if(value) {
            this.getTilePanelHealth().enable();

            this.renderPageContent(
                {'pk': value, 'full': true},
                'CIRDIRHealth',
                'renderer_document',
                this.getTilePanelHealth()
            );

        }
        else {
            this.getTilePanelHealth().setPageContent('');
            this.getTilePanelHealth().disable();
        }
    },

    renderPageContent: function(values, controller, method, tile) {
        if ( !tile.mask )
            tile.mask = new Ext.LoadMask(tile.getEl(), 'carregando informações...');

        if(tile._readRenderTID)
            Ext.Ajax.abort(tile._readRenderTID);

        tile.mask.show();
        tile.setPageContent('<p>Carregando conteúdo...</p>');

        if(!(typeof(values)===typeof({})))
            values = {'pk': values};

        tile._readRenderTID = Ext.Ajax.request({
            url: core.callAction(controller, method),
            params: values,
            method: 'GET',
            callback: function() {
                tile._readRenderTID = null;
                tile.mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    tile.setPageContent(rst.content);
                }
                else
                    tile.setPageContent([
                        '<p>Ocorreu um erro carregando o documento.</p>',
                        '<p>Mensagem: ' + rst.message + '</p>'
                    ].join(''));
            },
            failure: function(xhr) {
                tile.setPageContent('<p>Erro carregando informações do documento.</p>');
            }
        });
    },

    getTabHealth: function(cfg) {
        if(!this._tabHealth) {
            this._tabHealth = Ext._create('Ext.Panel', {
                title: 'SAÚDE',
                layout: 'form',
                frame: true,
                border: false,
                autoScroll: true,
                overflow: 'auto',
                bodyStyle: 'padding: 5px',
                height: 535,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getHealthGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 510,
                                border: false,
                                frame: false,
                                style: {marginLeft: '10px'},
                                autoScroll: true,
                                items: [
                                    this.getTilePanelHealth(),
                                ]
                            },
                        ]
                    },
                ],
            });
        }
        return this._tabHealth;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 125,
                        items: [
                            {
                                xtype:'fieldset',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'employee_unicode',
                                                hideLabel: true,
                                                // fieldLabel: 'Procurador/Promotor',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'tabpanel',
                        activeTab: 0,
                        border: false,
                        items: this.getItems(cfg),
                    },
                ]
            });
        }
        return this._formPanel;
    },

    getItems : function(cfg) {
        items = [];
        if (cfg.params.health_area) {
            items.push(this.getTabHealth(cfg));
            this.getHealthGrid(cfg).getSubmitAction().hide();
        } else {
            if (cfg.values.check_address) {
                items.push(this.getTabAddress(cfg));
            }
            if (cfg.values.check_teaching) {
                items.push(this.getTabTeaching(cfg));
            }
            if (cfg.values.check_property) {
                items.push(this.getTabProperty(cfg));
            }
            if (cfg.values.check_debits) {
                items.push(this.getTabDebits(cfg));
            }
            if (cfg.values.check_attach_irpf) {
                items.push(this.getTabIRPF(cfg));
            }
            if (cfg.values.check_health) {
                items.push(this.getTabHealth(cfg));
            }
        }
        return items;
    },

    getButtons: function() {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                      this.close();
                    }
                }
            ];
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        console.log(cfg.values.check_attach_irpf);
        corregedoria.cirdir.Window.superclass.constructor.call(this, cfg);
        if (this.oId) {
            if (cfg.params.health_area) {
                this.getHealthGrid(cfg).addFilterProperty('controlinformation_id', this.oId, 100, false);
                this.getHealthGrid(cfg).addFilterProperty('controlinformation__authorization_health', true, 101, true);
            } else {
                if (cfg.values.check_address) {
                    this.getAddressGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
                if (cfg.values.check_teaching) {
                    this.getTeachingGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
                if (cfg.values.check_property) {
                    this.getPropertyGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
                if (cfg.values.check_debits) {
                    this.getDebitsGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
                if (cfg.values.check_attach_irpf) {
                    this.getAttachIRPFGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
                if (cfg.values.check_health) {
                    this.getHealthGrid(cfg).setFilterProperty('controlinformation_id', this.oId, 100);
                }
            }
        }

    },

});
