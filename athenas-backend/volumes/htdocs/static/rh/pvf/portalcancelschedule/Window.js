Ext._define('rh.pvf.portalcancelschedule.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.pvf.portalcancelschedule.Restful',

    width:720,
    height:500,


    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        title: 'Programações',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            this.getUsufructGrid(cfg)
                        ]
                    },
                    {
                        title: 'Observação (Opcional):',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            {
                                name: "observation",
                                height:80,
                                width:670,
                                fieldLabel: "Observação (opcional)",
                                allowBlank: true,
                                hideLabel: true,
                                xtype: "textarea"
                            }
                        ]
                      
                    },    
                  
                ]
            });

        return this._formPanel;
    },


    getUsufructGrid: function (cfg) {
        if (!this._usufructGrid) {
            var sm = new Ext.grid.CheckboxSelectionModel({singleSelect:true});
            this._usufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 250,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['start_date', 'end_date', 'days','subtype_usufruct','type_activity','start_date_acquisition'],
                sm: sm,
                doubleClickHandler: function () { }
            });
            this._usufructGrid._columnModel.config.unshift(sm);
            this._usufructGrid.setFilterProperty('activity__acquisition_period__employee__pk',cfg.params.employee_id,1000,false)
            this._usufructGrid.setFilterProperty('status__in',cfg.params.cancel_status,1001,false)
            this._usufructGrid.setFilterProperty('activity__acquisition_period__group_period__configuration__sub_type_of_usufruct__in',cfg.params.cancel_usufruct,1002,false);
            this._usufructGrid.setFilterProperty('start_date__gte',new Date(new Date().setDate(new Date().getDate()-cfg.params.amount_past_days_for_cancel)).toISOString().slice(0, 10),1003);
            this._usufructGrid.getStore().on({
                scope: this,
                load: function () {
                    this.markModifieds(cfg, this._usufructGrid);
                }
            });
    
        }
        return this._usufructGrid;
    },

    markModifieds: function (cfg, grid) {
        var _data = grid.getStore().data;
        var modifieds = core.nullValue(cfg.usufructModifieds, []);
        if (cfg.action == 'update') {
            _data.items.map(function (item) {
                modifieds.push(item.data.pk);
            });
        }
        var _selected = [];
        for (i = 0; i <= modifieds.length; i++) {
            _data.items.map(function (item) {
                if (modifieds[i] != undefined && modifieds[i] == item.data.pk) {
                    _selected.push(item);
                }
            });
        }
        grid.getSelectionModel().clearSelections();
        grid.getSelectionModel().selectRecords(_selected);
    },

    getButtons: function (cfg) {
        if (!this._buttons) 
            this._buttons = []
            this._buttons.push(
                new Ext._create('Ext.Button', {
                    text:"Solicitar Cancelamento",
                    height: 28,
                    width:110,
                    scope: this,
                    handler: function () {
                        this.save(cfg);
                    },
                    
                }),
                new Ext._create('Ext.Button', {
                    text: 'Fechar',
                    height: 28,
                    scope: this,
                    handler: function () {
                        this.close();
                    },
                    
                })
            )
        return this._buttons;
    },

    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        selections= this.getUsufructGrid().getSelectionModel().getSelections()
        if(selections.length > 0) {
            params['usufruct_id'] = selections[0].get('pk')
        }else{
            params['usufruct_id'] = ''
        }    
        var rest = Ext._create('rh.pvf.portalcancelschedule.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});  
        mask.show();
        rest.doRequest(
            rest.getRoute('request_cancel', false, 'POST', {
                scope: this,
                params,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.ownerGrid.getStore().reload()
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        ); 

    }

});
   