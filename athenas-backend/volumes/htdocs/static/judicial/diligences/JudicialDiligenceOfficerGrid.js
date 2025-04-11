
Ext._define('judicial.diligences.JudicialDiligenceOfficerGrid', {
    extend: 'judicial.diligences.JudicialDiligenceGrid',

    restWindow: 'judicial.diligences.JudicialDiligenceOfficerWindow',

    configOrderToolBar: ['main', '-', 'search', 'openPrinter', '-', 'openLawsuit', '->'],

    openLawsuit: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var lawsuit = selected.get('out_court_lawsuit_pk');
            var width, height, left, top;

            width = (Ext.getBody().getBox().width * 0.9);
            height = (Ext.getBody().getBox().height * 0.9);
            left = screenX + (screen.width / 2) - (width / 2);
            top = (screen.height / 2) - (height / 2);

            var spec = [
                'width=' + width,
                'height=' + height,
                'top=' + top,
                'left=' + left,
                'scrollbars',
                'resizable',
                'status',
                'titlebar'
            ];

            if(this._wndP) this._wndP.close();

            this._wndP = window.open(
                '/athenas/EJudOutCourtLawsuit/viewer/#officer/0/' + lawsuit,
                'ejud-proccess',
                spec.join(', ')
            );

            if(!this._wndP)
                Ext.Msg.show({
                    title: 'Abrindo procedimento!',
                    msg: 'O bloqueador de popup interceptou a abertura do procedimento!',
                    buttons: Ext.Msg.OK,
                    icons: Ext.Msg.ERROR
                });

            this._wndP.config = function() {
                return selected.data;
            };

            this._wndP.MainRemoteObserver = core.RemoteObserver;
            this._wndP.getRemoteObserver = function() { return core.RemoteObserver; };
        }
        else
            Ext.Msg.show({
                title: 'Visualização Procedimento',
                msg: 'Primeiro selecione uma diligência para visualizar o procedimento.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getOpenLawsuitAction: function(cfg) {
        if(!this._openLawsuitAction)
            this._openLawsuitAction = Ext._create('Ext.Button', {
                text: 'Visualizar Procedimento',
                iconCls: 'icon-judicial icon-ejud-open-proccess',
                scope: this,
                handler: this.openLawsuit
            });

        return this._openLawsuitAction;
    },

    getResponseAction: function(cfg) {
        if(!this._responseAction)
            this._responseAction = Ext._create('Ext.Button', {
                text: 'Responder Diligência',
                iconCls: 'icon-judicial icon-ejud-manifestation-direct',
                scope: this,
                handler: this.response
            });

        return this._responseAction;
    },

    response: function() {
        var selections = this.getSelectionModel().getSelections();

        if(selections.length > 0) {
            if (selections[0].data.response_is_signed_by_officer){
                Ext.Msg.show({
                    'title': 'Diligências Internas',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': 'Não é possével modificar uma diligência já assinada.'
                });
                return '';
            }else{
                selections[0].data.diligence = selections[0].data.pk;
                Ext._create('judicial.diligences.officer.ResponseWindow', {
                    action: 'create',
                    values: selections[0].data
                }).show();
                return '';
            }
        }
        else
            Ext.Msg.show({
                'title': 'Diligências Internas',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione uma Diligência!'
            });
            return '';
    },

    getMainAction: function(cfg) {
        if(!this._mainAction)
            this._mainAction = Ext._create('Ext.Button', {
                text: 'Ações',
                menu: [
                    this.getConfirmDistributionAction(cfg),
                    '-',
                    this.getReportAction(cfg)
                ]
            });

        return this._mainAction;
    },

    getConfirmDistributionAction: function(cfg) {
        if(!this._confirmDistributionAction)
            this._confirmDistributionAction = Ext._create('Ext.menu.Item', {
                text: 'Confirmar distribuição',
                iconCls: 'icon-judicial icon-ejud-confirm-diligence',
                scope: this,
                handler: this.acceptDiligence
            });

        return this._confirmDistributionAction;
    },

    getDownloadDocumentAction: function(cfg) {
        if(!this._downloadButtonAction)
            this._downloadButtonAction = Ext._create('Ext.menu.Item', {
                text: 'Download do documento',
                iconCls: 'icon-judicial icon-ejud-download-document',
                scope: this,
                handler: this.downloadDocument
            });

        return this._downloadButtonAction;
    },

    downloadDocument: function() {
        var selection = this.getSelectionModel().getSelected();

        if(selection && selection.get('permalink'))
            open(selection.get('permalink'), "_self");
        else if (selection)
            Ext.Msg.show({
                title: 'Fazendo download',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Esta diligencia não tem documento em anexo.'
            });
        else
            Ext.Msg.show({
                title: 'Fazendo download',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione a diligencia da qual quer fazer o download.'
            });
    },

    acceptDiligence: function(){
        var rest = Ext._create('judicial.diligences.officer.DiligenceRestful');
        var mask = new Ext.LoadMask(this.getEl(), {'msg': 'Processando...'});
        var selections = this.getSelectionModel().getSelections();

        if(selections.length > 0) {
            mask.show();
            rest.doRequest(
                rest.getRoute('accept_diligence', false, 'POST', {
                    scope: this,
                    params: {
                        pkset: selections.map(function(data) { return data.get('pk'); })
                    },
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            this.getStore().reload();
                            /**
                             * FIXME analizar quando estiver aceitando o lote se tem pelomenos uma diligencia classificada
                             * como interna.
                             **/
                            this.fireEvent('afterAcceptDiligence', { withInternal: true });
                        }
                        else
                            Ext.Msg.show({
                                title: 'Aceitando diligencias',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: 'Aceitando diligencias',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponivel no momento.'
                        });
                    }
                })
            );
        }
        else
            Ext.Msg.show({
                'title': 'Diligências',
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione pelo menos uma Diligência!'
            });
            return '';
    },

    constructor: function(cfg){
        cfg = cfg || {};

        judicial.diligences.JudicialDiligenceOfficerGrid.superclass.constructor.call(this, cfg);
    }
});
