Ext._define('rh.gfp.conference.payroll.EntriesGrid', {
    extend: 'core.RestfulGrid',

    configOrderToolBar: ['check', 'download'],

    rest: 'rh.gfp.conference.payroll.EntriesRestful',
    restWindow: 'rh.gfp.conference.payroll.EntriesWindow',


    getColumnModel: function() {
        if(!this._columnModel){
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: '', dataIndex: 'icons', sortable: true, width: 125, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: '', dataIndex: 'icons_previous', sortable: true, width: 125, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: 'Cod', dataIndex: 'pk', width: 80, hidden: true},
                    {header: 'Descrição', dataIndex: 'unicode', sortable: true, width: 290, id: 'autoExpandColumn'},
                    {header: "Mês/Ano Ref.", width: 80, dataIndex: 'reference', renderer: this.rendererReference, menuDisabled: true},
                    {header: 'Quantidade', dataIndex: 'qnt', width: 80, renderer:  this.rendererQnt, menuDisabled: true},
                    {header: 'Percentual', dataIndex: 'pct', width: 70, menuDisabled: true },
                    {header: 'Prazo', dataIndex: 'prazo_desc', width: 120, menuDisabled: true },
                    {header: 'Valor Base (R$)', dataIndex: 'valor_base', width: 90, renderer: this.rendererBaseValue, menuDisabled: true },
                    {header: 'Valor (R$)', dataIndex: 'valor', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                    {header: 'Valor(R$)', dataIndex: 'correct_valor', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                    {header: 'Patronal (R$)', dataIndex: 'patronal', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                    {header: 'Patronal Devido (R$)', dataIndex: 'correct_patronal', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true}
                ]
            );
        }
        return this._columnModel;
    },
 

    getFooterbar: function(cfg){
        if(!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                style: cfg.footerStyle,
                store: this.getStore(),
                pageSize: 50,
                items: [
                    this.getProventosTextItem(),
                    this.getDescontosTextItem(),
                    this.getLiquidoTextItem(),
                    this.getPatronalTextItem(),
                ]
            });

        this.getStore().on({
                scope: this,
                load: function(st, records, options, grid){
                    var valor = 0;
                    var patronal = 0;
                    var desconto = 0;
                    var status = 1;

                    st.each(
                        function(record) {
                            if(record.get('event_type') == 'P')
                                valor += record.get('valor');
                            else
                                desconto += record.get('valor');

                            patronal += record.get('patronal');
                        }
                    );
                    this.updateInfoValuesPaycheck(valor, desconto, patronal, (valor - desconto));
                }
            });

        return this._footerbar;
    },

    getProventosTextItem: function(){
        if(!this.proventosText){
            this.proventosText= new Ext.Toolbar.TextItem({
                text: 'Proventos: R$ 0,00',
                width: 135,
                style: {
                    'color': '#15428B',
                    'font-weight': 'bold',
                    'font-size':'10px'
                }
            });
        }
        return this.proventosText;
    },

    rendererQnt: function(value, p, r){
        var st = r.data['status'];
        var qnt = 0;
        var qnt_max = 0;
        if (st == 'CT' || st == 'CE') {
            qnt = r.data['qnt']
            qnt_max = r.data['qnt_max']

        } else {
            qnt = r.data['correct_qnt'];
            qnt_max = r.data['correct_qnt_max'];
        }
        var desc = (qnt != qnt_max && qnt_max != 0) ? qnt+'/'+qnt_max : qnt;
        return desc;
    },

    rendererBaseValue: function(value, p, r){
        var st = r.data['status'];
        var base_value = (st == 'CT' || st == 'CE')? r.data['valor_base']: r.data['correct_base_value'];
        return toolkit.util.formatCurrency(base_value);
    },

    rendererReference: function(value, p, r){
        var zero = r.data['reference_month'] < 10 ? '0' : '';
        return zero + r.data['reference_month'] + "/" + r.data['reference_year'];
    },

    viewConfig: {
        stripeRows: false,
        getRowClass: function(record, index, rowParams, store){
            style = (record.data.tipo == 'PROVENTO'? 'prov-entry': 'desc-entry');
            style += (record.data.status_entry == 'NC'? ' nc-entry': '');
            return style;
        }
    },

    // userTextToolBar: function(){
    // 	if(!this._userTextToolBar){
    // 		this._userTextToolBar = new Ext.form.DisplayField({
    // 			value: '',
    // 			width: 200,
    // 		});
    // 	}
    // 	return this._userTextToolBar;
    // },

    updateInfoToolBar: function(){
    	rec = this.getSelectionModel().getSelected();
   		//this._userTextToolBar.setValue(rec? rec.data.modified_by_unicode + ' - ' + rec.data.modified_at.format("d/m/Y h:i"): '');
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-esocial icon-balloon-exclamation',
                tooltip: 'Mensagem',
                scope: this,
                handler: function(action, index) {
                	if(!this.getSelectionModel().isSelected(index))
                		this.getSelectionModel().selectRow(index);
                	this.messageWindow(index);
                }
            },
        ];
    },

    generateConsolidatedPaycheck: function(){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'RelatorioContracheque',
                'generate_report'
            ),
            params: {
                start: this._paycheck.folha_unicode.split('-')[0].trim(),
                end:'',
                employee: this._paycheck.servidor
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Holerite Consolidado',
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                  
            }, 
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
       
    },

    generatePaycheck: function(){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(
                'RelatorioContracheque',
                'generate_report'
            ),
            params: {
                paycheck:this._paycheck.pk
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Holerite',
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                   
            }, 
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
       
    },

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.payroll.EventGrid.superclass.getConfigActionsItems.call(this, cfg);

        menu['check'] = {
                text: 'Conferir',
                iconCls: 'icon-core icon-core-success',
                scope: this,
                handler: this.checkEntriesPaycheck
        };
        menu['differences'] = {
                text: 'Ver Pagamentos',
                iconCls: 'icon-rh icon-core-banking-data-tab',
                scope: this,
                handler: this.viewDifferences
        };
        menu['paycheck_print'] = {
                text: 'Gerar Contra Cheque',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                handler: generatePaycheck
        };
        menu['consolidated_paycheck'] = {
            text: 'Gerar Holerite Consolidado',
            iconCls: 'icon-core icon-core-select',
            scope: this,
            handler:this.generateConsolidatedPaycheck
        };
        menu['add-entry'] = {
                text: 'Gerar Contra Cheque',
                iconCls: 'icon-core icon-core-reports',
                scope: this,
                handler: function() {
                    paycheck_report = Ext._create('rh.gfp.paycheck.reports.PayCheck');
                    paycheck_report._paycheck = this._paycheck;
                    paycheck_report.generate();
                }
        };
        return menu;
    },

    viewDifferences: function(){
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var grid = Ext._create('rh.gfp.paycheckdifference.EntryDifferenceShowGrid', {
                baseParams: {entry: selected.get('pk')},
            });

            var wnd = Ext._create('Ext.Window', {
                title: 'Pagamentos de Diferenças',
                modal: true,
                border: false,
                width: 750,
                height: 450,
                layout: 'fit',
                items: [grid]
            });

            wnd.show();
        }
        else
            Ext.Msg.show({
                title: 'Diferenças',
                msg: 'Primeiro selecione um item.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    _updatePaycheck: function(){
        this.getStore().on({
                scope: this,
                load: function(st, records, options, grid){
                    var valor = 0;
                    var patronal = 0;
                    var desconto = 0;
                    var status = 1;

                    st.each(
                        function(record) {
                            if(record.get('event_type') == 'P')
                                valor += record.get('valor');
                            else
                                desconto += record.get('valor');

                            patronal += record.get('patronal');
                        }
                    );
                    this.updateInfoValuesPaycheck(valor, desconto, patronal, (valor - desconto));
                }
            });
    },

    checkEntriesPaycheck: function(){
        var sels = this.getSelectionModel().getSelections();
        var pks = [];
        var lm = new Ext.LoadMask(this.getEl(), {'msg': 'Conferindo lançamentos...'});
        var paycheckGrid = this.baseParams.grid
        var EntriesGrid = this.baseParams.EntriesGrid

        if(sels.length > 0) {
            Ext.Msg.show({
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja conferir os lançamentos selecionados?',
                scope: this,
                fn: function(b) {
                    if(b == 'no') return;
                    lm.show();
                    Ext.each(sels, function(item) {pks.push(item.get('pk'));});
                    Ext.Ajax.request({
                        'url': toolkit.util.Normalize.controller_action('GFPConferenceEntries', 'checked'),
                        'disableCaching': false,
                        'params': {'entries': pks, 'paycheck': this._paycheck.pk,'payroll':this._paycheck.folha},
                        'method': 'POST',
                        'success': function(request) {
                            var obj = Ext.decode(request.responseText);
                            lm.hide();
                            // if(obj.message) {
                            //     Ext.MessageBox.show({
                            //        title: 'Conferir',
                            //        msg: obj.message,
                            //        buttons: Ext.MessageBox.OK,
                            //        icon: obj.success? Ext.MessageBox.INFO: Ext.MessageBox.ERROR
                            //     })
                            // }
                            if(obj.success)
                                this.getStore().load({});
                                EntriesGrid.getStore().load({})
                                //paycheckGrid.getStore().load({})
                        },
                        'failure': function(request) {
                            lm.hide();
                            Ext.MessageBox.show({
                               title: 'Erro',
                               msg: 'Ocorreu um erro inesperado',
                               buttons: Ext.MessageBox.OK,
                               icon: Ext.MessageBox.ERROR
                            });
                        },
                        'scope': this
                    });
                }
            });
        }
        else Ext.Msg.show({
            'title': 'Confirmação de lançamentos',
            'msg': 'Selecione os lançamentos a serem conferidos!',
            'buttons': Ext.Msg.OK,
            'icon': Ext.Msg.WARN
        });
    },

    messageWindow: function(index) {
        var entry = this.getStore().getAt(index).data;

        new rh.gfp.payroll.PayrollMessageWindow({
            action: (entry.message ? 'update' : 'create'),
            values: 'remote',
            oId: entry.message,
            params: {
                entry: entry.pk,
            },
            callback: {
                success: {
                    scope: this,
                    fn: function(args) {
                        this.getStore().load();
                    }
                }
            },
        }).show();
    },

    updateInfoValuesPaycheck: function(proventos, descontos, patronal, liquido) {
        this.getProventosTextItem().setText('Proventos: R$ ' + Ext.util.Format.number(proventos ? proventos : 0.0, '0.0,00/i'));
        this.getDescontosTextItem().setText('Descontos: ' + Ext.util.Format.number(descontos ? descontos : 0.0, '0.0,00/i'));
        this.getLiquidoTextItem().setText('Liquido: R$ ' + Ext.util.Format.number(liquido ? liquido : 0.0, '0.0,00/i'));
        this.getPatronalTextItem().setText('Patronal: R$ ' + Ext.util.Format.number(patronal ? patronal : 0.0, '0.0,00/i'));
    },

    getDescontosTextItem: function(){
        if(!this.descontosText){
            this.descontosText= new Ext.Toolbar.TextItem({
                text: 'Descontos: R$ 0,00',
                width: 135,
                style: {
                    'color': '#FF0000',
                    'font-weight': 'bold'
                }
            });
        }
        return this.descontosText;
    },

    getLiquidoTextItem: function(){
        if(!this.liquidoText){
            this.liquidoText= new Ext.Toolbar.TextItem({
                text: 'Líquido: R$ 0,00',
                width: 135,
                style: {
                    'color': '#14950E',
                    'font-weight': 'bold'
                }
            });
        }
        return this.liquidoText;
    },

    getPatronalTextItem: function(){
        if(!this.patronalText){
            this.patronalText= new Ext.Toolbar.TextItem({
                text: 'Patronal: R$ 0,00',
                width: 135,
                style: {
                    // 'color': '#FF0000',
                    'font-weight': 'bold'
                }
            });
        }
        return this.patronalText;
    },

   

   

});

core.RestfulGrid.register(
    'rh.gfp.conference.payroll.EntriesRestful',
    'rh.gfp.conference.payroll.EntriesGrid'
);