var app = angular.module('Debt', []);

app.controller('DebtCtrl', function ($scope, RestService) {
    $scope.names = [
        'Val',
        'Marty'
    ];

    $scope.name = $scope.names[0];
    $scope.owedTo = $scope.names[1];
    $scope.amount = '';
    $scope.date = new Date();
    $scope.notes = '';
    $scope.debts = null;

    $scope.submit = function () {
        RestService.addNewDebt($scope.name, $scope.owedTo, $scope.amount, $scope.date, $scope.notes).success(function (data) {
            $scope.debts.push(data.debt);
        });
    };

    RestService.getAllDebts().success(function (data, status, headers, config) {
        $scope.debts = data.debts;
    });
});

app.service('RestService', function ($http, $q) {
    function getDate(millisecondsSinceEpoch) {
        var tzMinutes = new Date().getTimezoneOffset();
        var tzMilliseconds = tzMinutes * 60 * 1000;
        return new Date(tzMilliseconds + millisecondsSinceEpoch);
    }

    this.getAllDebts = function () {
        return $http.get('/api/debts').success(function (data) {
            for (var i = 0; i < data.debts.length; i++) {
                var debt = data.debts[i];
                debt.date = getDate(debt.date);
            }
        });
    };

    this.addNewDebt = function (name, owedTo, amount, date, notes) {
        try {
            amount = parseFloat(amount);
            amount = parseInt(amount * 100);
        } catch (e) {
            return $q.reject(e);
        }

        debt = {
            name: name,
            owed_to: owedTo,
            amount: amount,
            date: date.valueOf(),
            notes: notes
        };
        return $http.post('/api/debts', debt).success(function (data) {
            data.debt.date = getDate(data.debt.date);
        });
    }
});