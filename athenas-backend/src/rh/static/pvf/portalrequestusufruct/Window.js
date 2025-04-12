
Ext._define('rh.pvf.portalrequestusufruct.Window', {
    extend: 'core.RestfulWindow',
    //extend: 'rh.pvf.portalrequest.Window',

    rest: 'rh.pvf.portalrequestusufruct.Restful',

    width:850,
    height:700,


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
                    [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg),this.getTabHistory(cfg)]:
                    [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg),this.getTabHistory(cfg)]
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
              
                    this.getAcquisitionPeriodFieldSet(cfg),  
                    {
                        title: 'Informações:',
                        xtype: 'fieldset',
                        border: true,
                        hidden:cfg.action == "update" ? false : true,
                        items:[
                            {
                                xtype: 'panel',
                                layout: 'column',
                                border: true,
                                items: [{ 
                                    columnWidth: .6,
                                    layout: 'form',
                                    items: [{
                                        fieldLabel: 'Período Aquisitivo',
                                        xtype: 'displayfield',
                                        anchor: '100%',
                                        hideLabel: true,
                                        name:'acquisitive_period'
                                    }]
                                },

                                {
                                    columnWidth: .4,
                                    layout: 'form',
                                    items: [{
                                        fieldLabel: 'Situação',
                                        xtype: 'displayfield',
                                        anchor: '100%',
                                        name:'status_display'
                                    }]
                                },
                                {
                                    columnWidth: .6,
                                    layout: 'form',
                                    items: [{
                                        fieldLabel: 'Servidor',
                                        xtype: 'displayfield',
                                        anchor: '100%',
                                        name:'employee_unicode'
                                    }]
                                },
                                {
                                    columnWidth: .4,
                                    layout: 'form',
                                    items: [{
                                        fieldLabel: 'Tipo da Solicitação',
                                        xtype: 'displayfield',
                                        anchor: '100%',
                                        name:'type_of_request'
                                    }]
                                },
                                
                                
                                ]
                            }
                            
                        ]
                         
                    },
                    {
                        title: 'Programações a serem alteradas',
                        xtype: 'fieldset',
                        border: true,
                        hidden:cfg.action == "update" ? false : true,
                        items:[
                            this.getBookedUsufructGrid(cfg),
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
                                width:800,
                                disabled:!cfg.values.check_status_update & cfg.action=="update"?true:false,
                                fieldLabel: "Observação (opcional)",
                                allowBlank: true,
                                hideLabel: true,
                                xtype: "textarea"
                            }
                        ]
                      
                    },

                ]
            });

        return this._managementPanel;
    },

    getAcquisitionPeriodFieldSet: function (cfg) {
        if (!this._acquisition)
            this._acquisition = Ext._create('Ext.form.FieldSet', {
                title: 'Saldos Disponíveis',
                hidden:cfg.action == "create" ? false : true,
                items: [
                    this.getAcquisitionPeriodGrid(cfg)
                ]
            });

        return this._acquisition;
    },

    getAcquisitionPeriodGrid: function (cfg) {
        if (!this._acquisitionPeriodGrid) {
            this._acquisitionPeriodGrid = Ext._create('rh.dayoff.acquisitionperiod.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 160,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['unicode_full_group_period', 'status_display', 'days', 'start_date_fruition', 'days_not_booked_cache', "start_date_acquisition", "end_date_acquisition"],
                doubleClickHandler: function () { }
            });

            this._acquisitionPeriodGrid.setSortProperty('group_period__year_reference','ASC',false);
            this._acquisitionPeriodGrid.setFilterProperty('group_period__configuration__sub_type_of_usufruct', cfg.values.type_of_usufruct_id, 1000, false);
            this._acquisitionPeriodGrid.setFilterProperty('days_not_booked_cache__gt',0, 1006,false);
            this._acquisitionPeriodGrid.setFilterProperty('status__in',[2,8],1004,false),
            this._acquisitionPeriodGrid.setFilterProperty('end_date_fruition__gte',new Date().toISOString().slice(0, 10),1002,false),
            this._acquisitionPeriodGrid.setFilterProperty('end_date_fruition',null,1002,false)
            this._acquisitionPeriodGrid.setFilterProperty('employee__pk', cfg.values.employee_id, 1005);


        }
        return this._acquisitionPeriodGrid;
    },

    getSubstitutePanel: function (cfg) {
        if (!this._substitutePanel)
            this._substitutePanel = Ext._create('Ext.Panel', {
                title: 'Substituto',
                layout:"form",
                frame: true,
                border: false,
                height: 428,
                width:650,
                items: [

                    {
                        xtype: 'fieldset',
                        title: 'Substitutos',
                        layout:"form",
                        hidden: cfg.action == "update"?false:true,
                        border: true,
                        items:[
                           this.getSubstituteFormPanel(cfg)
                        ]
                    },        

                    {
                        xtype: 'fieldset',
                        title: 'Adicionar Substituto',
                        layout:"form",
                        hidden:cfg.action == 'update'?true:false,
                        border: true,
                        items:[
                            this.getSubstitute(cfg),
                            this.getExercise(cfg),
                            //this.getProvison(cfg),
                            this.getStartDate(),
                            this.getFinalDate(),
                            {
                                xtype: 'fieldset',
                                border: false,
                                items: [
                                    this.getButtonSubstitute(cfg),
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Substitutos',
                        hidden:cfg.action == 'update'?true:false,
                        layout:"form",
                        border: true,
                        items:[
                            this.getSubstituteGrid(cfg)
                        ]
                    },    
                   
                  
                ]
            });
            // if(cfg.params){
            //     if(cfg.params.responsible){
            //         this._substitutePanel.enable();
            //     }else{
            //         this._substitutePanel.disable();
            //     }
            // }else{
            //     this._substitutePanel.enable();
            // }
        this._substitutePanel.disable();
        return this._substitutePanel;
    },

    getSubstitute: function (cfg) {
        if (!this._substitute){
            this._substitute = Ext._create('core.fields.AutocompleteField',{
                    xtype: "rest-autocompletefield",
                    fieldLabel: "Substituto",
                    allowBlank: true,
                    rest: "rh.employee.Restful",
                    name: "substitute",
                });

                this._substitute.setPreFilter([
                    {
                        property: 'ativo',
                        value: true,
                        stage: 0,
                    },
                    {
                        property: 'tipo',
                        value: cfg.params.type_employee,
                        stage: 1,
                    },
                ]);

        }

        return this._substitute;
    },

    setSubstituteFilter: function(cfg, absence_date=null) {
        /**
         * Define o filtro de substituição com base nas configurações fornecidas.
         *
         * @param {Object} cfg - Objeto de configuração contendo os parâmetros necessários.
         * @param {Date|null} absence_date - Data de ausência (opcional).
         */
        const bookingStore = this.getBookingStore();
        const items = bookingStore.data.items;
        if (items.length > 0 || absence_date != null) {
            if (absence_date != null){
                var dataFormatada = absence_date.toISOString().split('T')[0];
            } else {
                const menorDatesPorItem = items.map(function(item) {
                    return item.data.start_date;
                });
            
                const dates = menorDatesPorItem.map(function(dateString) {
                    const [day, month, year] = dateString.split('/');
                    return new Date(`${year}-${month}-${day}`);
                });
            
                const menorData = new Date(Math.min.apply(null, dates));
            
                var dataFormatada = menorData.toISOString().split('T')[0];
            }
          const preFilter = [
            {
              property: 'ativo',
              value: true,
              stage: 0,
            },
            {
              property: 'designacao',
              value: true,
              stage: 1,
            },
            {
              property: 'servidor__tipo',
              value: cfg.params.type_employee,
              stage: 2,
            },
            {
              property: 'servidor__pk',
              value: cfg.params.employee_id,
              stage: 3,
            }
          ];
      
          if (cfg.params.type_employee === "M") {
            preFilter.push(
              {
                property: 'responsible',
                value: true,
                stage: 5,
              },
              {
                property: 'pk__in',
                value: cfg.params.movimentacoes_posse,
                stage: 6,
              },
              {
                property: 'owner',
                value: true,
                stage: 7,
              },
              {
                property: 'lotacao__electoral_zone',
                value: false,
                stage: 8,
              }
            );
          } else {
            preFilter.push(
              {
                property: 'movimentacao_posse__quadro__cargo__chefia',
                value: true,
                stage: 4,
              }
            );
          }
      
          preFilter.push(
            {
              property: 'data_vigencia_fim__gt',
              value: dataFormatada,
              stage: 555,
            },
            {
              property: 'data_vigencia_fim__isnull',
              value: true,
              stage: 555,
            }
          );
      
          this._exercise.setPreFilter(preFilter);
          this.getExercise().getComboField().getStore().load();
        }
      },

    getExercise: function (cfg) {
        if (!this._exercise){
            this._exercise = Ext._create('core.fields.AutocompleteField',{
                    xtype: "rest-autocompletefield",
                    fieldLabel: "Exercício",
                    allowBlank: true,
                    readOnly:cfg.params.exercise_one?true:false,
                    value:cfg.params.exercise_one?cfg.params.exercise_one:null,
                    rest: "rh.employee.workplace.Restful",
                    name: "exercise",
                    gridConfig: {
                        columnAction: false,
                        hideItemsToolbar:['add', 'remove', 'edit', 'download', '-', 'setMain'],
                    }
                });

                if(cfg.params.type_employee == "M"){
                    this._exercise.setPreFilter([
                        {
                            property: 'ativo',
                            value: true,
                            stage: 0,
                        },
                        {
                            property: 'designacao',
                            value: true,
                            stage: 1,
                        },
                        {
                            property: 'servidor__tipo',
                            value: cfg.params.type_employee,
                            stage: 2,
                        },
                        {
                            property: 'servidor__pk',
                            value: cfg.params.employee_id,
                            stage: 3,
                        },
                        {
                            property:'responsible',
                            value:true,
                            stage:5
                            
                        },
                        {
                            property:'pk__in',
                            value:cfg.params.movimentacoes_posse,
                            stage:6
                            
                        },
                        {
                            property:'owner',
                            value:true,
                            stage:7
                            
                        },
                        {
                            property:'lotacao__electoral_zone',
                            value:false,
                            stage:8
                        }

                    ]);
                }else{
                    this._exercise.setPreFilter([
                        {
                            property: 'ativo',
                            value: true,
                            stage: 0,
                        },
                        {
                            property: 'designacao',
                            value: true,
                            stage: 1,
                        },
                        {
                            property: 'servidor__tipo',
                            value: cfg.params.type_employee,
                            stage: 2,
                        },
                        {
                            property: 'servidor__pk',
                            value: cfg.params.employee_id,
                            stage: 3,
                        },
                        {
                            property: 'movimentacao_posse__quadro__cargo__chefia',
                            value: true,
                            stage: 4,
                        },

                    ]);
                }

                
        }
        return this._exercise;
    },

    getStartDate: function (cfg) {
        if (!this._startDate)
            this._startDate = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data in\u00edcio",
                allowBlank: true,
                //minValue:(new Date()).format('d/m/Y'),
                width: 320,
                enableKeyEvents: true,
            });
        return this._startDate;
    },
    getFinalDate: function (cfg) {
        if (!this._finalDate)
            this._finalDate = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data Fim",
                allowBlank: true,
                //minValue:(new Date()).format('d/m/Y'),
                width: 320,
                enableKeyEvents: true,
            });
        return this._finalDate;
    },

    addSubstitute:function(cfg,params){
        var row = new this._recordField({
            start_date:params.start_date ,
            end_date: params.end_date,
            substitute_id: params.substitute_id,
            exercise_id:params.exercise_id,
            substitute:this.getSubstitute()._comboField.lastSelectionText,
            exercise:this.getExercise()._comboField.lastSelectionText,
        });
        this.getSubstituteStore().add(row);
        this.getStartDate().setValue(null)
        this.getFinalDate().setValue(null)
        if (!cfg.params.exercise_one)
            this.getExercise().setValue(null)
        this.getSubstitute().setValue(null)
    },


    getButtonSubstitute: function (cfg) {
        if (!this._buttonSubstitute) {
            this._buttonSubstitute = Ext._create('Ext.Button', {
                text: 'Adicionar Substituto',
                height: 30,
                scope: this,
                handler: function () {
                    //var period_start_date = Ext.util.Format.date(this.getInitialDate().getValue(), 'd/m/Y')
                    var days = this.getDays().getValue()
                    var start_date=  Ext.util.Format.date(this.getStartDate().getValue(), 'd/m/Y')
                    var end_date =  Ext.util.Format.date(this.getFinalDate().getValue(), 'd/m/Y')
                    var substitute_id = this.getSubstitute().getValue()
                    var exercise_id = this.getExercise().getValue()
                    if(!start_date || !end_date || !substitute_id || !exercise_id){
                        Ext.Msg.show({
                            title: 'Error',
                            msg: "Preencha todos os campos corretamente.",
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        })
                       
                    }else{
                        this.validateSubstitute(cfg,{
                            //'period_start_date': period_start_date,
                            'days': days,
                            'start_date':start_date,
                            'end_date':end_date,
                            'substitute_id':substitute_id,
                            'exercise_id':exercise_id
                        })
                        
                    }   

                    
                }
            });
        }
        return this._buttonSubstitute;
    },


    getSubstituteFormPanel: function (cfg) {
        if (!this._substituteGrid)
            this._substituteGrid = Ext._create('rh.pvf.portalrequestsubstitute.Grid', {
                region: 'center',
                disabled:cfg.action == "update"?false:true,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['start_date', 'end_date', 'substitute_unicode','exercise_unicode'],
                border: false,
                scope: this,
                height: 120,
                doubleClickHandler: function () { },
                request_id:cfg.values.pk,
                columnAction: false,
            });
        this._substituteGrid.setFilterProperty('portal_request__pk', cfg.values.pk)
        return this._substituteGrid;
    },

    getSubstituteGrid: function (cfg) {
        if (!this._gridSubstitute)
            this._gridSubstitute = new Ext.grid.GridPanel({
                store: [],
                height: 120,
                store: this.getSubstituteStore(),
                columns: [
                    { header: 'Substituto', dataIndex: 'substitute', width: 200 },
                    { header: 'Exercicio', dataIndex: 'exercise', width: 200 },
                    { header: 'Data Início', dataIndex: 'start_date', width: 80 },
                    { header: 'Data Fim', dataIndex: 'end_date', width: 80 },
                    { header: 'substitute_id', dataIndex: 'substitute_id', width: 80,hidden:true },
                    { header: 'exercise_id', dataIndex: 'exercise_id', width: 80,hidden:true },
                   
                    {
                        xtype: 'actioncolumn', id: '', scope: this,
                        width:80,
                        items: [
                            {
                                iconCls: 'icon-16px icon-core icon-core-delete',
                                tooltip: 'Remover item.',
                                scope: this,
                                handler: function (grid, row, col) {
                                    this.getSubstituteStore().removeAt(row);
                                }
                            }
                        ]
                    },
                   

                ]
            });

        return this._gridSubstitute;
    },

    getSubstituteStore: function () {
        if (!this._storeSubstitute) {
            this._storeSubstitute = new Ext.data.Store({
                reader: new Ext.data.JsonReader({ fields: this.getSubstituteRecord() }),
                //sortInfo: { field: 'start_date', direction: 'ASC' }
            });
        }

        return this._storeSubstitute;

    },

    getSubstituteRecord: function () {
        if (!this._recordSubstituteField) {
            this._recordSubstituteField = Ext.data.Record.create([
                { name: 'start_date', type: 'date', dateFormat: 'd/m/Y', },
                { name: 'end_date', type: 'date', dateFormat: 'd/m/Y', },
                { name: 'substitute' },
                { name: 'exercise'},
                //{ name: 'provision'},
                { name: 'substitute_id' },
                { name: 'exercise_id'}
            ]);
        }

        return this._recordSubstituteField
    },


    getHistoryGrid: function(cfg) {
        if(!this._historyGrid) {
            this._historyGrid = Ext._create('rh.pvf.portalrequesthistory.Grid',{
                hideItemsToolbar: ['remove', 'download','add','edit'],
                columnAction: false,
                allowCreate: false,
                allowRemove: false,
                allowUpdate: false,
                region: 'center',
                border: false,
                scope: this,
                height: 300,
                columnAction: false,
            });
        }
        this._historyGrid.setFilterProperty('portal_request', cfg.values.pk)
        return this._historyGrid;
    },

    getTabObservation: function(cfg) {
        if(!this._tabObservation)
            this._tabObservation = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Observação(Opcional)',
                iconCls: '',
                border: false,
                frame: true,
                scope: this,
                hidden:true,
                autoHeight: true,
                items: [
                    {
                        name: "observation",
                        fieldLabel: "Observação (opcional)",
                        height:120,
                        width:772,
                        allowBlank: true,
                        hideLabel: true,
                        xtype: "textarea"
                    },
                ]
            });
        return this._tabObservation;
    },

    getTabHistory: function(cfg) {
        if(!this._tabAddress)
            this._tabAddress = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Histórico',
                iconCls: '',
                border: false,
                frame: true,
                scope: this,
                autoHeight: true,
                items: [
                    this.getHistoryGrid(cfg)
                ]
            });
        this._tabAddress.disable()
        return this._tabAddress;
    },

    setButtonDisable:function(cfg){
        if(cfg.action == "update"){
            if(!cfg.values.check_status_update){
                return true
            }else{
                return false
            } 
        }else{
            return false
        }
         
    },

    
    getButtons: function (cfg) {
        if (!this._buttons) 
            this._buttons = []
            this._buttons.push(
                new Ext._create('Ext.Button', {
                    text:cfg.action == "create" ?'Criar Solicitação':"Atualizar Solcitação",
                    height: 28,
                    hidden:cfg.action == "update"?true:false,
                    disabled:this.setButtonDisable(cfg),
                    width:110,
                    scope: this,
                    handler: function () {
                        this.save(cfg);
                    },
                    
                }),
                new Ext._create('Ext.Button', {
                    text: 'Fechar',
                    hidden:cfg.action == "update"?true:false,
                    height: 28,
                    scope: this,
                    handler: function () {
                        this.close();
                    },
                    
                })
            )
        return this._buttons;
    },

    setAddButtonSale:function (cfg) {
        if(cfg.values.configuration[cfg.values.type_of_usufruct_id]){
            if(cfg.values.configuration[cfg.values.type_of_usufruct_id]['sale'] > 0){
                return this.getAddButtonSale(cfg)
            }else{
                return this.getAddButtonSale(cfg).setDisabled(true)
            }
        }else{
            return this.getAddButtonSale(cfg)
        }
       
    },

    setDisabledPortionField:function(cfg){
        if (cfg.values.type_employee == "M"){
            if((cfg.values.configuration[cfg.values.type_of_usufruct_id]) && cfg.values.type_of_usufruct_id ==9001 ){ //Somente férias individuais
                if(cfg.values.configuration[cfg.values.type_of_usufruct_id]['sale'] > 0){
                    return false
                }else{
                    return true
                }
            }else{
                return true
            }
        }else{
            return true
        }
            
    },
   

//Configuração de Períodos - Início

    getNewBookField: function (cfg) {
        if (!this._newPeriods)
            this._newPeriods = Ext._create('Ext.form.FieldSet', {
                title: 'Preencha os campos e clique em Incluir',
                layout: 'hbox',
                //hidden:cfg.action == "update"?true:false,
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Início',
                        border: false,
                        width: 150,
                        defaults: {
                            defaults: { margins: '0 0 5 0' },
                        },
                        items: [
                            this.getInitialDate(cfg),
                            this.getWeekdayInitialDisplay()
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Dias',
                        border: false,
                        width: 100,
                        items: [
                            this.getDays(cfg)
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Fim',
                        border: false,
                        width: 100,
                        items: [
                            this.getEndDate(),
                            this.getWeekdayEndDisplay()
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Nº Parcelas Indenizado',
                        border: false,
                        hidden:this.setDisabledPortionField(cfg)?true:false,
                        width: 100,
                        items: [
                           this.getPortion(cfg)
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        border: false,
                        padding: 5,
                        items: [
                            this.getAddButton(cfg)
                        ]
                    },

                    {
                        xtype: 'fieldset',
                        border: false,
                        padding: 5,
                        items: [
                            this.setAddButtonSale(cfg)
                        ]
                    },
                    
                ]
            });

        return this._newPeriods;
    },

    getNewBookSaleField: function () {
        if (!this._newPeriodssale)
            this._newPeriodssale = Ext._create('Ext.form.FieldSet', {
                title: 'Nova Parcela (Venda) - Preencha a quantidade de dias e clique em Vender ',
                layout: 'hbox',
                items: [
                    {
                        
                        title: 'Dias',
                        xtype: 'fieldset',
                        border: false,
                        margin:screenLeft,
                        items: [
                            this.getDaysSale()
                        ]
                        
                    },   
                    {
                        xtype: 'fieldset',
                        border: false,
                        padding: 5,
                        items: [
                            this.getAddButtonSale()
                        ]
                    },
                    
                ]
            });

        return this._newPeriodssale;
    },

    getInitialDate: function (cfg) {
        if (!this._initial)
            this._initial = Ext._create('Ext.form.DateField', {
                hideLabel: true,
                //minValue:(new Date()).format('d/m/Y'),
                disabled:!cfg.values.check_status_update & cfg.action=="update"?true:false,
                width: 130,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    change: function () {
                        this.getEndDisplay();
                        this.setWeekday();
                    }
                }
            });
        return this._initial;
    },

    getWeekdayInitialDisplay: function () {
        if (!this._weekdayInitial)
            this._weekdayInitial = Ext._create('Ext.form.DisplayField', {
                hideLabel: true,
            });

        return this._weekdayInitial;
    },


    getEndDate: function () {
        if (!this._enddate)
            this._enddate = Ext._create('Ext.form.DisplayField', {
                hideLabel: true,
                height: 18
            });

        return this._enddate;
    },

    getWeekdayEndDisplay: function () {
        if (!this._weekdayEnd)
            this._weekdayEnd = Ext._create('Ext.form.DisplayField', {
                hideLabel: true,
            });

        return this._weekdayEnd;
    },

    filtereSale:function(value){
        return value.data.activity != "Marcação"
    },

    validateFields:function(start_date,days){
        if(!start_date && !days){
            Ext.Msg.show({
                title: 'Error',
                msg: "Informe‌ ‌início‌ ‌e‌ ‌quantidade‌ ‌de‌ ‌dias.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }else if(start_date && !days || !start_date && days ){
            Ext.Msg.show({
                title: 'Error',
                msg: "Em‌ ‌uma‌ ‌das‌ ‌programações‌ ‌informadas,‌ ‌não‌ ‌foi‌‌ informado‌ ‌início‌ ‌e/ou‌ ‌quantidade‌ ‌de‌ ‌dias.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        
        }
    },

    validateFieldsSale:function(days,book){
        value = book.filter(this.filtereSale)
        if(!days){
           return true
        }
        else if (value.length > 0 && ![9007, 9005, 9004, 9002, 9008].includes(this.getParams().type_of_usufruct_id)){
            return true
        } else{
            return false
        }
    },

    validateMensageSale:function(days,book){
        value = book.filter(this.filtereSale)
        if(!days){
            return Ext.Msg.show({
                title: 'Error',
                msg: "Informe‌ a ‌quantidade‌ ‌de‌ ‌dias.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
           
        }
        else if (value.length > 0){
            return Ext.Msg.show({
                title: 'Error',
                msg: "É‌ ‌permitido‌ ‌somente‌ ‌uma‌ ‌venda‌ ‌por‌‌ solicitação.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getAddButton: function (cfg) {
        if (!this._addButton) {
            this._addButton = Ext._create('Ext.Button', {
                text: 'Incluir Usufruto',
                height: 30,
                disabled:!cfg.values.check_status_update & cfg.action=="update"?true:false,
                scope: this,
                handler: function () {
                    start_date = this.getInitialDate().getValue()
                    days = this.getDays().getValue()
                    if(!start_date && !days || start_date && !days || !start_date && days){
                        this.validateFields(start_date,days)
                    }else{
                        var row = new this._recordField({
                            start_date: Ext.util.Format.date(this.getInitialDate().getValue(), 'd/m/Y'),
                            end_date: this.getEndDate().getValue(),
                            days: this.getDays().getValue(),
                            sale_usufruct:0,
                            activity: 'Marcação'
                        });
                        this.getBookingStore().add(row);
                        this.getDays().setValue(null)
                        this.getInitialDate().setValue(null)  
                        this.getEndDate().setValue(null)
                        this.getWeekdayInitialDisplay().setValue(null)
                        this.getWeekdayEndDisplay().setValue(null)
                        if (cfg.params.responsible)
                            this.getSubstitutePanel().enable()
                        this.setSubstituteFilter(cfg)
                    } 
                   
                   
                }
            });
        }
        return this._addButton;
    },

    getAddButtonSale: function (cfg) {
        if (!this._addButtonSale) {
            this._addButtonSale = Ext._create('Ext.Button', {
                text: 'Incluir Venda',
                height: 30,
                width:60,
                disabled:!cfg.values.check_status_update & cfg.action=="update"?true:false,
                scope: this,
                handler: function () {
                    var book = this.getBookingStore().data.items
                    var days = this.getDays().getValue()
                    
                    if(this.validateFieldsSale(days,book)){
                        this.validateMensageSale(days,book)
                    }else{
                        var portion = null
                        if (cfg.values.type_of_usufruct_id ==9007){
                            portion = 1
                        }
                        else if (this.getPortion().getValue()){
                            portion = this.getPortion().getValue()
                        } else if(cfg.values.type_employee == "M"){
                            portion = 1
                        }
                        var row = new this._recordField({
                            days: this.getDays().getValue(),
                            sale_usufruct:1,
                            activity: 'Venda',
                            portion: portion
                        });
                        this.getBookingStore().add(row);
                        this.getDays().setValue(null)
                        this.getInitialDate().setValue(null)
                        this.getEndDate().setValue(null)
                        this.getWeekdayInitialDisplay().setValue(null)
                        this.getWeekdayEndDisplay().setValue(null)
                    }
                  
                   
                }   
            });
        }
        return this._addButtonSale;
    },

    setWeekday: function () {
        if (this.getInitialDate().getValue() != '' && this.getDays().getValue() > 0) {
            this.getWeekdayInitialDisplay().setValue(this.getWeekday(this.getInitialDate().getValue()));
            this.getWeekdayEndDisplay().setValue(this.getWeekday(Date.parseDate(this.getEndDate().getValue(), 'd/m/Y')));
        }
    },


    getEndDisplay: function () {
        if (this.getInitialDate().getValue() != '' && this.getDays().getValue() > 0) {
            data = Date.parseDate(this.getInitialDate().value, 'd/m/Y');
            data.setDate(data.getDate() + (parseInt(this.getDays().getValue() - 1)));
            this.getEndDate().setValue(Ext.util.Format.date(data, 'd/m/Y'));
        }
    },

    getPortion: function (cfg) {
        if(!this._portionField)
        this._portionField = Ext._create('standard.fields.ChoiceField', {
            name: 'portion',
            hiddenName: 'portion',
            hideLabel: true,
            value:cfg.values.type_employee == "M"? cfg.values.type_of_usufruct_id==9001?2:null:null,
            width:70,
            choiceId: 'pvf.PARCEL_NUMBER',
        });

        return this._portionField;
    },

    getDays: function (cfg) {
        if (!this._days)
            this._days = Ext._create('Ext.form.NumberField', {
                width: 70,
                hideLabel: true,
                disabled:!cfg.values.check_status_update & cfg.action=="update"?true:false,
                enableKeyEvents: true,
                listeners: {
                    scope: this,
                    change: function (text, event) {
                        this.getEndDisplay();
                        this.setWeekday();
                    }
                }
            });

        return this._days;
    },

    getDaysSale: function () {
        if (!this._dayssale)
            this._dayssale = Ext._create('Ext.form.NumberField', {
                width: 120,
                hideLabel: true,
                enableKeyEvents: true,
            });

        return this._dayssale;
    },


    getNewBook: function (cfg) {
        if (!this._booked)
            this._booked = Ext._create('Ext.form.FieldSet', {
                title: 'Programações',
                //hidden:cfg.action == "update"?true:false,
                items: [
                    this.getBookingGrid(cfg)
                ]
            });

        return this._booked;
    },

    checkSaleUsufruct:function(bookStore,responsible){
        var checked = false
        data = bookStore.data.items
        function checkStore(item) {
            if (item.data.sale_usufruct == 0)
                checked = true
        }
        data.forEach(checkStore);
        if (!checked && responsible)
            this.getSubstitutePanel().disable()
        
    },

    getBookingGrid: function (cfg) {
        if (!this._gridMarkings)
            this._gridMarkings = new Ext.grid.GridPanel({
                store: [],
                height: 100,
                autoExpandColumn: 'autoExpandColumn',
                store: this.getBookingStore(),
                columns: [
                    { header: 'Atividade', dataIndex: 'activity', width: 120 },
                    { header: 'Inicio', dataIndex: 'start_date', width: 80 },
                    { header: 'Fim', dataIndex: 'end_date', width: 80 },
                    { header: 'Dias', dataIndex: 'days', width: 80 },
                    { header: 'Parcelas', dataIndex: 'portion', width: 80},
                   
                    {
                        xtype: 'actioncolumn', id: '', scope: this,
                        width:80,
                        items: [
                            {
                                iconCls: 'icon-16px icon-core icon-core-delete',
                                tooltip: 'Remover item.',
                                scope: this,
                                handler: function (grid, row, col) {
                                    this.getBookingStore().removeAt(row);
                                    this.checkSaleUsufruct(this.getBookingStore(),cfg.params.responsible)
                                }
                            }
                        ]
                    },
                    {
                        xtype: 'actioncolumn', id: 'autoExpandColumn', scope: this,
                        width:80,
                        hidden:true,
                        items: [
                            {
                                iiconCls: true,
                                icon: '/' + global.Context + '/static/rh/images/folha-recalcular.png',
                                tooltip: 'Vender',
                                scope: this,
                                handler: function (grid, row, col) {
                                    this.sale_usufruct(row)
                                }
                            }
                        ]
                    }

                ]
            });

        return this._gridMarkings;
    },



    getBookingStore: function () {
        if (!this._storeMarking) {
            this._storeMarking = new Ext.data.Store({
                reader: new Ext.data.JsonReader({ fields: this.getBookingRecord() }),
                sortInfo: { field: 'start_date', direction: 'ASC' }
            });
        }

        return this._storeMarking;

    },

    getBookingRecord: function () {
        if (!this._recordField) {
            this._recordField = Ext.data.Record.create([
                { name: 'start_date', type: 'date', dateFormat: 'd/m/Y', },
                { name: 'end_date', type: 'date', dateFormat: 'd/m/Y', },
                { name: 'days' },
                { name: 'activity'},
                { name: 'portion'}
            ]);
        }

        return this._recordField
    },

    getBookedUsufructsFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Programações a serem alteradas',
                width: 570,
                items: [
                    this.getBookedUsufructGrid(cfg)
                ]
            });

        return this._marked;
    },

    getBookedUsufructGrid: function (cfg) {
        if (!this._bookedUsufructGrid) {
            var sm = Ext._create('Ext.grid.CheckboxSelectionModel');
            this._bookedUsufructGrid = Ext._create('rh.dayoff.usufruct.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 150,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns: ['start_date', 'end_date', 'days'],
                sm: sm,
                doubleClickHandler: function () { }
            });

            this._bookedUsufructGrid._columnModel.config.push(sm);
            this._bookedUsufructGrid.setFilterProperty('activity__activity_requests__id', cfg.values.pk,1000);
            this._bookedUsufructGrid.getStore().on({
                scope: this,
                load: function () {
                    this.markModifieds(cfg, this._bookedUsufructGrid);
                }
            });
        }
        return this._bookedUsufructGrid;
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

    getWeekday: function (date) {
        var weekday = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sabado']
        return weekday[date.getDay()]
    },

    validateSubstitute:function(cfg,params){
        var rest = Ext._create('rh.pvf.portalrequestsubstitute.Restful', {});
        rest.doRequest(
            rest.getRoute('validate_substitute', false, 'GET', {
                scope: this,
                params,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if (rst.new_end_date){
                        params['end_date'] = rst.new_end_date;
                    }
                    if(rst.success) {
                        this.addSubstitute(cfg,params)
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
    },

    setStoreSubstitute:function(store){
        substitutes_data =[]
        store.each(function(rec){
            substitutes_data.push(
                {
                    start_date: rec.get('start_date'),
                    end_date: rec.get('end_date'),
                    substitute:rec.get('substitute_id'),
                    exercise:rec.get('exercise_id'),
                    provision:rec.get('provision')

                }
            )
        });
        return substitutes_data
    },

    setDataUsufructIn:function(store,total_days,parcel_number,usufructs_in){
        var total_days = 0;
        var parcel_number = 0
        usufructs_in = []
        store.each(function (rec) {
            total_days = total_days+rec.get('days')
            parcel_number = rec.get('portion')?parcel_number+rec.get('portion'):0
            usufructs_in.push(
                {
                    start_date: rec.get('start_date'),
                    end_date: rec.get('end_date'),
                    days:rec.get('days'),
                    sale_usufruct:rec.get('sale_usufruct')

                }
            )
        });
        return {
            'usufructs_in':usufructs_in,
            'total_days':total_days,
            'parcel_number':parcel_number
        }
    },

    save: function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        var store = this.getBookingStore()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        var data_usufructs =  this.setDataUsufructIn(store)
        var rest = Ext._create('rh.pvf.portalrequestusufruct.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});
        params['type_usufruct'] = cfg.values.type_of_usufruct_id
        params['usufructs_in'] = JSON.stringify(data_usufructs.usufructs_in)
        params['substitutes'] = JSON.stringify(substitutes_data)
        params['pk'] = cfg.values.pk
        params['total_days'] = data_usufructs.total_days
        params['parcel_number'] = data_usufructs.parcel_number
        mask.show();
        rest.doRequest(
            rest.getRoute('save_usufruct', false, 'POST', {
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
    },



});

