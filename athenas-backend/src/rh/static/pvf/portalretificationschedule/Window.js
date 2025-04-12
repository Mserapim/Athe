Ext._define('rh.pvf.portalretificationschedule.Window', {
    extend: 'rh.pvf.portalrequestusufruct.Window',

    rest: 'rh.pvf.portalretificationschedule.Restful',

    width:800,
    height:800,


    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg),
                submit_all_checks: true
            });

        return this._formPanel;
    },


    getTabPanel: function (cfg) {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 900,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    cfg.action == "create"?
                    [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg)]:
                    [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg)]
                ]
            });

        return this._tabPanel;
    },

    getManagerPanel: function (cfg) {
        if (!this._managementPanel)
            this._managementPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                title: 'Principal',
                layout: 'form',
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
                        title: 'Usufrutos Selecionados',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            this.labelUsufruct(), 
                        ]
                      
                    },  
                    this.getNewBookField(cfg),
                    this.getNewBook(cfg),

                    {
                        title: 'Observação (Opcional):',
                        xtype: 'fieldset',
                        border: true,
                        items:[
                            {
                                name: "observation",
                                height:80,
                                width:750,
                                fieldLabel: "Observação (opcional)",
                                allowBlank: true,
                                hideLabel: true,
                                xtype: "textarea"
                            }
                        ]
                      
                    },    
                   
                ]
            });

        //this.disabledButtons(cfg)  
        return this._managementPanel;
    },


    // getFormPanel: function (cfg) {
    //     if (!this._formPanel)
    //         this._formPanel = Ext._create('Ext.form.FormPanel', {
    //             border: false,
    //             frame: true,
    //             items: [
                   
                  
    //             ]
    //         });
        
    //     this.disabledButtons(cfg)
    //     return this._formPanel;
    // },

    getSelectionIds: function(){
        var sm = this.getSelModel();
        var selecteds = []
        Ext.each(
            sm.getSelections(), 
            function(item, idx, all){
                selecteds.push(item);
            },
            this
            )                    
        return selecteds;
    },

    setAddButtonSale:function (cfg) {
        if(cfg.params.type_employee == "M"){
            return this.getAddButtonSale(cfg)
        }else{
            return this.getAddButtonSale(cfg).setDisabled(true)
        }
            
    },


    saleButtonDisabled:function(items){
        sale = false
        items.forEach(
            function(item) {
                if(item.data.sale_usufruct) {
                    sale = true
                }
            }
        );
        return sale
    },

    filterUsufructEqualAcquisitionPeriod:function(acquisition_period_id, item){
        var scope= this;
        values= scope.getUsufructGrid().getStore().data.items

        items = []
        for (var i = 0; i < values.length; i++) {
            if(values[i].data.acquisition_period == acquisition_period_id){
                if (values[i].data.subtype_id == 9001 || values[i].data.subtype_id == 9000){
                    items.push(values[i])
                }
                else{
                    items.push(item)
                }
            }
        }
        return items
    },

    isSelectionActivity:function(selections,activity_id){
        for (var i = 0; i < selections.length; i++) {
          if(selections[i].data.activity !== activity_id)
            return true
        }
        return false
    },

   
    getSelModel: function(cfg){
        if(!this.selModel){
            var scope= this;
            var cfg = cfg;
            this.selModel = new Ext.grid.CheckboxSelectionModel({
                checkOnly:false,
                deselectRow: function(row, preventViewNotify) {
                    var ref = this
                    if(ref.isLocked()){
                        return;
                    }
                    if(ref.last == row){
                        ref.last = false;
                    }
                    if(ref.lastActive == row){
                        ref.lastActive = false;
                    }
                    if(ref.locked == row){
                        ref.locked = false;
                    }
                    items = scope.selModel.selections.items
                    items.forEach(
                        function(item){
                            var row = scope.getUsufructGrid().getStore().find('pk', item.data.pk);
                            var r =ref.grid.store.getAt(row);
                            if(!preventViewNotify){
                                ref.grid.getView().onRowDeselect(row);
                            } 
                            ref.fireEvent('rowdeselect', ref, row, r);
                            ref.fireEvent('selectionchange', ref);
                        }     
                    )
                    ref.selections.clear();   

                },
                selectRow:function(row, keepExisting, preventViewNotify){
                    var ref = this
                    acquisition_period_id = ref.grid.store.getAt(row).data.acquisition_period
                    item = ref.grid.store.getAt(row);
                    items = []
                
                        if(cfg.params.type_employee == "M"){
                            items = scope.filterUsufructEqualAcquisitionPeriod(acquisition_period_id, item)
                        }else{
                            items.push(item)

                        }                        
                    var count = 0
                    items.forEach(
                        function(item){
                            var row = scope.getUsufructGrid().getStore().find('pk', item.data.pk);
                            data_selections = scope.getUsufructGrid().getSelectionModel().getSelections()
                            var r =ref.grid.store.getAt(row);
                            if(r && ref.fireEvent('beforerowselect', ref, row, keepExisting, r) !== false){
                                if (scope.isSelectionActivity(data_selections,item.data.activity))
                                    ref.clearSelections()
                                ref.selections.add(r);
                                ref.last = ref.lastActive = row;
                                if(!preventViewNotify){
                                    ref.grid.getView().onRowSelect(row);
                                }
                                if(!ref.silent){
                                    ref.fireEvent('rowselect', ref, row, r);
                                    ref.fireEvent('selectionchange', ref);
                                }
                            }
                            count = count+1
                        }
                        
                    )
                },  
                listeners:{
                    rowselect: function(sm, index, record) {
                        var values = scope.getSelectionIds();
                        var sale = scope.saleButtonDisabled(values)
                        scope.labelUsufruct().setValue(scope.setValueLabel(values));
                        // scope.getAddButton(cfg).setDisabled(false)
                        // if(sale)
                        //     scope.setAddButtonSale(cfg).setDisabled(false)
                    },
                    rowdeselect: function(sm, index, record) {
                        scope.labelUsufruct().setValue("")
                        // scope.getAddButtonSale(cfg).setDisabled(true)
                        // scope.getAddButton(cfg).setDisabled(true)
                        
                    },

                },
            });
        }
        return this.selModel;
    },

    setValueLabel:function(values){
        days = 0
        usufruct = ''
        values.forEach(
            function(item) {
               days = days+item.data.days
               usufruct = item.data.subtype_usufruct
            }
        );

        return days+" Dias de "+usufruct+" selecionado para retificação."

    },

    labelUsufruct: function () {
        if (!this._usufruct)
            this._usufruct = Ext._create('Ext.form.DisplayField', {
                hideLabel: true,
                height: 18
            });

        return this._usufruct;
    },

    getUsufructGrid: function (cfg) {
        if (!this._usufructGrid) {
            this._usufructGrid = Ext._create("rh.pvf.portalusufructretification.Grid", {
                region: 'south',
                gridAutoLoad: true,
                height: 200,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['start_date', 'end_date', 'days','subtype_usufruct','type_activity','start_date_acquisition'],
                sm: this.getSelModel(cfg),
                doubleClickHandler: function () { }
            });
            this._usufructGrid._columnModel.config.unshift(this.getSelModel(cfg));
    
        }
        return this._usufructGrid;
    },

    
    disabledButtons:function(cfg){
        this.getAddButtonSale(cfg).setDisabled(true)
        this.getAddButton(cfg).setDisabled(true)
    },
    

    getButtons: function (cfg) {
        if (!this._buttons) 
            this._buttons = []
            this._buttons.push(
                new Ext._create('Ext.Button', {
                    text:"Solicitar Retificação",
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

    setDataUsufructSelections:function(selections){
        var usufruct_ids = []
        var days_usufructs = 0
        var usufruct_all = []
        selections.forEach(
            function(item) {
                if(item.data.type_activity != "Venda"){
                    usufruct_ids.push(item.data.pk)
                    days_usufructs = days_usufructs+item.data.days
                }
                usufruct_all.push(item.data.pk)
            }
        );
        return {
            'usufruct_ids':usufruct_ids,
            'days_usufructs':days_usufructs,
            'usufruct_all':usufruct_all
        }
    },

    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        selections= this.getUsufructGrid().getSelectionModel().getSelections()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        var store = this.getBookingStore()
        var data_selections = this.setDataUsufructSelections(selections)
        var data_usufructs =  this.setDataUsufructIn(store)
        params['modifieds'] = JSON.stringify(data_selections.usufruct_ids)
        params['all_modifieds'] = JSON.stringify(data_selections.usufruct_all)
        params['usufructs_in'] = JSON.stringify(data_usufructs.usufructs_in)
        params['total_days']=data_usufructs.total_days
        params['parcel_number'] = data_usufructs.parcel_number
        params['substitutes'] = JSON.stringify(substitutes_data)
        params['days_usufructs'] = data_selections.days_usufructs
        var rest = Ext._create('rh.pvf.portalretificationschedule.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});  
        mask.show();
        rest.doRequest(
            rest.getRoute('request_retification', false, 'POST', {
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
   