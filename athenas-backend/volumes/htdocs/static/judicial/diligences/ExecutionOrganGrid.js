
Ext._define('judicial.diligences.ExecutionOrganGrid', {
    extend: 'judicial.diligences.JudicialDiligenceGrid',

    configOrderToolBar: ['openDocument', '-', 'assumeDelivery', '-', 'finishDiligence', '-', 'search', '->'],

    restWindow: 'judicial.diligences.ExecutionOrganWindowRestful',

    getAssumeDeliveryAction: function(cfg) {
        if(!this._assumeDeliveryAction)
            this._assumeDeliveryAction = Ext._create('Ext.Button', {
                text: 'Assumir Entrega',
                iconCls: 'icon-judicial icon-ejud-triage-effectivate',
                scope: this,
                handler: function() {
                    this.assumeDelivery();
                }
            });

        return this._assumeDeliveryAction;
    },

    getFinishDiligenceAction: function() {
        if (!this._finishDiligenceAction) {
            this._finishDiligenceAction = Ext._create('Ext.Button', {
                text: 'Finalizar',
                iconCls: 'icon-agree icon-agree-close-supervisor',
                scope: this,
                handler: function() {
                    this.finishDiligence();
                }
            });
        }

        return this._finishDiligenceAction;
    },

    assumeDelivery: function() {
        var selected = this.getSelectionModel().getSelections();
        var mask;


        if(selected.length > 0) {
            mask = new Ext.LoadMask(this.getEl(), {msg: 'assumindo entrega...'});

            Ext.Msg.show({
                title: 'Assumindo a entrega',
                msg: 'Tem certeza que deseja assumir a entrega das diligencias selecionadas?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn === 'no') return;

                    mask.show();
                    this.factoryRestful().assumeDelivery(
                        selected.map(function(d) { return d.get('pk'); }),
                        {
                            scope: this,
                            fn: function() {
                                this.getStore().reload();
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Assumindo a entrega',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            fn: function() { mask.hide(); }
                        }
                    );
                }
            });
        }
        else
            Ext.Msg.show({
                title: 'Assumindo a entrega',
                msg: 'Nenhuma diligencia foi selecionada para ser assumida.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getOpenDocumentAction: function(cfg) {
        if(!this._openDocumentAction)
            this._openDocumentAction = Ext._create('Ext.Button', {
                text: 'Abrir Procedimento',
                iconCls: 'icon-judicial icon-ejud-open-proccess',
                scope: this,
                handler: this.openDocument
            });

        return this._openDocumentAction;
    },

    openDocument: function() {
        var selected = this.getSelectionModel().getSelected();
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
            '/athenas/EJudOutCourtLawsuit/viewer/#' + selected.get('out_court_lawsuit_pk'),
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
    },

    finishDiligence: function() {
        var selected = this.getSelectionModel().getSelections();
        var mask;

        if (selected.length > 0) {
            mask = new Ext.LoadMask(this.getEl(), {msg: 'Finalizando...'});

            Ext.Msg.show({
                title: 'Finalizar diligência',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza de que deseja finalizar essa(s) diligência(s)?',
                scope: this,
                fn: function(btn) {
                    if (btn == "no") return;

                    mask.show();
                    this.factoryRestful().finishDiligence(
                        selected.map(function(d) { return d.get('pk'); }),
                        {
                            scope: this,
                            fn: function(obj) {
                                Ext.Msg.show({
                                    title: this.title,
                                    icon: obj.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: obj.message
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: this.title,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: message
                                });
                            }
                        },
                        {
                            fn: function() { mask.hide(); }
                        }
                    );
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Finalizar diligência',
                msg: 'Nenhuma diligencia foi selecionada para ser finalizada.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Diligências em edição',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleStatus(1); }
                },
                {
                    text: 'Aguardando Distribução para os Oficiais',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleStatus(2); }
                },
                {
                    text: 'Aguardando Confirmação de Recebimento pelo Oficial',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleStatus(3); }
                },
                {
                    text: 'Entrega em andamento',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleStatus(4); }
                },
                {
                    text: 'Entrega Concluída',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleStatus(5); }
                },
                {
                    text: 'Solicitado publicação em Diário Oficial',
                    checked: true,
                    scope: this,
                    handler: function() { this.toggleStatus(6); }
                },
                {
                    text: 'Entrega sendo realizada no Órgão de Execução',
                    checked: true,
                    scope: this,
                    handler: function() { this.toggleStatus(7); }
                },
                '-',
                {
                    text: 'Diligências com e sem manifestação',
                    checked: true,
                    scope: this,
                    group: 'manifestation',
                    handler: function() { this.toggleManifestation(); }
                },
                {
                    text: 'Apenas diligências com manifestação',
                    checked: false,
                    scope: this,
                    group: 'manifestation',
                    handler: function() { this.toggleManifestation(false); }
                },
                {
                    text: 'Apenas diligências sem manifestação',
                    checked: false,
                    scope: this,
                    group: 'manifestation',
                    handler: function() { this.toggleManifestation(true); }
                },
                '-',
            ];

        return this._filterMenu;
    },

});

core.RestfulGrid.register(
    'judicial.diligences.ExecutionOrganRestful',
    'judicial.diligences.ExecutionOrganGrid'
);
